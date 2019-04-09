fabric:
  pip.installed:
    - name: fabric <= 2.4.0
    - user: root
    - require:
      - pkg: python3-pip
      - pkg: python3-dev
    - bin_env: '/usr/bin/pip3'
