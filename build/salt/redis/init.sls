install-redis:
  pkg.installed:
    - name: redis-server
  host.present:
    - ip: 127.0.0.1
    - names:
        - redis

/etc/redis/redis.conf:
  file.managed:
    - user: redis
    - group: redis
    - source: salt://redis/files/redis.conf
    - template: jinja
    - require:
      - pkg: install-redis
