postgresql:
  pkg:
    - installed
  host.present:
    - ip: 127.0.0.1
    - names:
        - db
