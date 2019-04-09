djgen_environment:
  file.managed:
    - name: /etc/environment
    - source: salt://webapps/djgen/files/environment/environment
    - template: jinja

/etc/uwsgi/apps-enabled/djgen.ini:
  file.managed:
    - user: webapps
    - group: root
    - makedirs: True
    - source: salt://webapps/djgen/files/uwsgi/djgen.ini
    - template: jinja
    - require:
      - user: webapps
      
/etc/nginx/sites-enabled/djgen:
  file.managed:
    - user: root
    - group: root
    - makedirs: True
    - source: salt://webapps/djgen/files/nginx/djgen
    - template: jinja

# /etc/nginx/ssl/djgen.pem:
#   file.managed:
#     - user: root
#     - group: root
#     - makedirs: True    
#     - contents_pillar: sslcerts:domainkey

/etc/systemd/system/uwsgi-djgen.service:
  file.managed:
    - user: root
    - group: root
    - makedirs: True
    - source: salt://webapps/djgen/files/uwsgi/uwsgi.service
    - require:
      - user: webapps
      - file: /var/log/uwsgi

djgen-db:
  postgres_database.present:
    - name: {{ salt['pillar.get']('database:dbname', '') }}
    - encoding: UTF8
    - owner: {{ salt['pillar.get']('database:user', '') }}
  host.present:
    - ip: 127.0.0.1
    - names:
        - {{ salt['pillar.get']('database:host', '') }}

djgendbuser:
  postgres_user.present:
    - name: {{ salt['pillar.get']('database:user', '') }}
    - password: {{ salt['pillar.get']('database:password', '') }}
