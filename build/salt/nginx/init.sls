nginx:
  pkg.installed:
    - name: nginx
  service.running:
    - enable: True

/etc/nginx/nginx.conf:
  file:
    - managed
    - source: salt://nginx/files/nginx.conf
    - user: root
    - group: root
    - mode: 644

/etc/nginx/sites-enabled/default:
  file.absent
