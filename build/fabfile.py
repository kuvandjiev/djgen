from fabric import Connection
from fabric import task
from shutil import copy
import yaml
import tarfile
import os


def check_for_valid_config(conf):
    """ Returns True if all required fields are presented in the `conf` dictionary.
        Will raise RuntimeError if something is missing
    """
    required = ('application_name', 'deployment_user', 'repository', 'deployment_targets', 'target_branch', )

    def check_key(key):
        val = conf.get(key)
        if not val:
            raise RuntimeError(f'Please specify {key} in the configuration. Currently you have entered {val}')

    for key in required:
        check_key(key)

    return True


def ceck_for_certs(cert_dir, username):
    """ Checks if the required public and private key for the user can be found """
    if not os.path.exists(cert_dir):
        raise RuntimeError(f"The directory {cert_dir} is missing. Please created one that contains all required users private and public keys.")

    private_key = os.path.join(cert_dir, username)
    if not os.path.exists(private_key):
        raise RuntimeError(f"The private key for user {username} can not be found at {private_key}")

    public_key = os.path.join(cert_dir, f"{username}.pub")
    if not os.path.exists(public_key):
        raise RuntimeError(f"The public key for user {username} can not be found at {public_key}")


BUILD_DIR = os.path.abspath(os.path.dirname(__file__))
DEPLOYMENT_CONFIG_FILE = os.path.join(BUILD_DIR, 'deployment_config.yml')

if not os.path.exists(DEPLOYMENT_CONFIG_FILE):
    raise RuntimeError(f'{DEPLOYMENT_CONFIG_FILE} can not be found. You can find a template in deployment_config_defaults.yml')

conf = yaml.load(open(DEPLOYMENT_CONFIG_FILE))
check_for_valid_config(conf)

APPLICATION_NAME = conf.get('application_name')
DEPLOYMENT_USER = conf.get('deployment_user')
REPOSITORY = conf.get('repository')
TARGETS = conf.get('deployment_targets')
TARGETS_BRANCH = conf.get('target_branch')

DEFAULT_SALT_DIR = os.path.join(BUILD_DIR, 'salt')
DEFAULT_SALT_PILLAR_DIR = os.path.join(BUILD_DIR, 'salt-pillar')
CERT_DIR = os.path.join(DEFAULT_SALT_DIR, 'cert')


DEPLOYMENT_ROOT = f'/webapps/{APPLICATION_NAME}'
REMOTE_BUILD_TOOLS_DIR = f'/webapps/{APPLICATION_NAME}/build'


# TODO: provision celery and supervisor


@task
def provision(c, target, salt_dir=DEFAULT_SALT_DIR, salt_pillar_dir=DEFAULT_SALT_PILLAR_DIR):
    """ provisions a target host using the configuration in config_dir"""

    ceck_for_certs(CERT_DIR, DEPLOYMENT_USER)
    SSH_KEY = os.path.join(CERT_DIR, DEPLOYMENT_USER)

    if target not in TARGETS.keys():
        print(f"Target {target} not found!")
        exit()

    host = TARGETS.get(target)
    with Connection(host) as conn:
        conn.run('wget -O salt_bootstrap.sh https://bootstrap.saltstack.com')
        conn.run('sudo sh salt_bootstrap.sh -x python3 -P -D')

        print("Transferring salt...")
        with tarfile.open('./salt.tar.gz', mode='w:gz') as arch:
            arch.add(salt_dir, recursive=True, arcname='./salt/')
        conn.put('./salt.tar.gz', '/tmp/salt.tar.gz')
        os.remove('./salt.tar.gz')
        conn.sudo('tar -xvzf /tmp/salt.tar.gz -C /tmp/')
        conn.sudo('rm -rf /srv/salt')
        conn.sudo('chmod 640 /tmp/salt -R')
        conn.sudo('mv /tmp/salt /srv/')
        conn.sudo('rm /tmp/salt.tar.gz')

        print("Transferring salt-pillar...")
        with tarfile.open('./salt-pillar.tar.gz', mode='w:gz') as arch:
            arch.add(salt_pillar_dir, recursive=True, arcname='./pillar/')
        conn.put('./salt-pillar.tar.gz', '/tmp/salt-pillar.tar.gz')
        os.remove('./salt-pillar.tar.gz')
        conn.sudo('tar -xvzf /tmp/salt-pillar.tar.gz -C /tmp/')
        conn.sudo('chmod 640 /tmp/pillar -R')
        conn.sudo('rm /tmp/salt-pillar.tar.gz')
        conn.sudo('rm -rf /srv/pillar')
        conn.sudo('mv /tmp/pillar /srv/pillar')

        print("Setting up minion")
        new_minion = os.path.join(salt_dir, f'minion-{target}')
        copy(os.path.join(salt_dir, 'minion'), new_minion)
        with open(new_minion, 'r') as f:
            minion = f.read()
            minion = minion.replace('{{env}}', target)
        with open(new_minion, 'w') as f:
            f.write(minion)
        conn.put(new_minion, '/tmp/minion')
        conn.sudo('mv /tmp/minion /etc/salt/minion')
        os.remove(new_minion)

        print("Calling highstate")
        conn.sudo('salt-call state.highstate')

    print("Provisioning done. Checking out the project")
    with Connection(host, user=DEPLOYMENT_USER, connect_kwargs={"key_filename": SSH_KEY}) as conn:
        if conn.run(f'test -d {DEPLOYMENT_ROOT}/.git', warn=True).failed:
            print("Cloning...")
            conn.run(f'git clone {REPOSITORY} {DEPLOYMENT_ROOT}/')

        print("Uploading latest fabfile...")
        conn.put(os.path.join(BUILD_DIR, 'fabfile.py'), '/tmp/')
        conn.sudo(f'mv /tmp/fabfile.py {REMOTE_BUILD_TOOLS_DIR}/')
    print("Done")


@task
def deploy(c, target, branch=None):
    ceck_for_certs(CERT_DIR, DEPLOYMENT_USER)
    SSH_KEY = os.path.join(CERT_DIR, DEPLOYMENT_USER)

    if target not in TARGETS.keys():
        print(f"Target {target} not found!")
        exit()

    host = TARGETS.get(target)
    if branch is None:
        branch = TARGETS_BRANCH.get(target)

    if input(f"TARGET: {target}\nBranch: {branch}\nDeploying to {host}\nDEPLOYMENT_ROOT: {DEPLOYMENT_ROOT}\nUser {DEPLOYMENT_USER}\nContinue [y,N]?") not in ['y', 'Y', ]:
        exit()

    with Connection(host, user=DEPLOYMENT_USER, connect_kwargs={"key_filename": SSH_KEY}) as conn:
        conn.put(DEPLOYMENT_CONFIG_FILE, REMOTE_BUILD_TOOLS_DIR)
        print("Executing:", f'fab -r {REMOTE_BUILD_TOOLS_DIR} remotedeploy {branch}')
        conn.run(f'fab -r {REMOTE_BUILD_TOOLS_DIR} remotedeploy {branch}')


@task
def remotedeploy(c, branch):
    """ pulls latest changes from {branch} and executes all necessary following procedures"""

    with c.cd(DEPLOYMENT_ROOT):
        if not os.path.exists(f"{DEPLOYMENT_ROOT}/.git"):
            clone(c)
    pull(c, branch)
    create_virtual_env(c)
    update_requirements(c)
    migrate(c)
    collectstatic(c)
    reloadapp(c, uwsgi=True, nginx=True)


@task
def clone(c):
    with c.cd(DEPLOYMENT_ROOT):
        c.run(f'git clone {REPOSITORY}')
        c.run('git pull')


@task
def create_virtual_env(c):
    with c.cd(DEPLOYMENT_ROOT):
        venv_dir = f"{DEPLOYMENT_ROOT}/env"
        if not os.path.exists(venv_dir):
            print(f"Creating virtual environment at {venv_dir}")
            c.run('virtualenv ./env --python=/usr/bin/python3')


@task
def update_requirements(c):
    with c.cd(DEPLOYMENT_ROOT):
        print('Updating requirements...')
        c.run('source ./env/bin/activate && pip install -r requirements.txt')
        c.run('source ./env/bin/activate && pip install uwsgi==2.0.18')


@task
def pull(c, branch):
    with c.cd(DEPLOYMENT_ROOT):
        c.run('git reset --hard')
        c.run('git pull')
        c.run(f'git checkout {branch}')


@task
def migrate(c):
    """ runs manage.py migrate """
    with c.cd(DEPLOYMENT_ROOT):
        print("Running migrate")
        c.run("python3 manage.py migrate --no-input", replace_env=False)


@task
def collectstatic(c):
    """ runs manage.py collectstatic """
    print("Running collectstatic")
    with c.cd(DEPLOYMENT_ROOT):
        c.run("python3 manage.py collectstatic --no-input", replace_env=False)


@task
def reloadapp(c, uwsgi=True, nginx=True):
    """ reloads uwsgi configuration, restarts nginx """
    print("Restarting services")
    if uwsgi:
        c.run(f"sudo service uwsgi-{APPLICATION_NAME} restart")
    if nginx:
        c.run("sudo service nginx restart")
