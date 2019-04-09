webapps-group:
  group.present:
    - name: webapps
        
webapps:
  user.present:
    - name: webapps
    - shell: /bin/bash
    - groups:
      - webapps
    - require:
      - group: webapps-group

deployer:
  user.present:
    - name: deployer
    - shell: /bin/bash
    - groups:
      - webapps
      - sudo
    - require:
      - group: webapps-group

/home/webapps/.ssh:
  file.directory:
    - user: webapps
    - group: root
    - require:
      - user: webapps

/home/deployer/.ssh:
  file.directory:
    - user: deployer
    - group: root
    - require:
      - user: deployer

deployerpkey:
  file.managed:
    - name: /home/deployer/.ssh/id_rsa
    - user: deployer
    - group: root
    - mode: 600
    - source: salt://cert/deployer
    - require:
      - user: deployer
      - file: /home/deployer/.ssh

deployerkey:
  ssh_auth:
    - present
    - user: deployer
    - enc: rsa
    - source: salt://cert/deployer.pub
    - require:
      - user: deployer
      - file: /home/deployer/.ssh

know_hosts:
  file.managed:
    - name: /home/deployer/.ssh/known_hosts
    - user: deployer
    - group: root
    - mode: 600
    - source: salt://users/files/known_hosts
    - require:
      - user: deployer
      - file: /home/deployer/.ssh

deployer-sudoer:
  file.append:
    - name: /etc/sudoers.d/deployer
    - text:
      - "deployer    ALL=(ALL)      NOPASSWD: ALL"

/var/log/webapps:
  file.directory:
    - user: webapps
    - group: webapps
    - makedirs: True
    - require:
      - user: webapps

/var/log/uwsgi:
  file.directory:
    - user: webapps
    - group: webapps
    - makedirs: True
    - require:
      - user: webapps
