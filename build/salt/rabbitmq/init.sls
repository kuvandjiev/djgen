rabbitmq-server:
  pkg:
    - installed
  host.present:
    - ip: 127.0.0.1
    - names:
        - rabbitmq

/etc/rabbitmq/rabbitmq.config:
  file.managed:
    - user: rabbitmq
    - group: rabbitmq
    - source: salt://rabbitmq/files/rabbitmq.conf
    - template: jinja
    - require:
      - pkg: rabbitmq-server
