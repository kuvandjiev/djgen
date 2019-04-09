wkhtmltox-deb:
  file.managed:
    - name: /tmp/wkhtmltox_0.12.5-1.bionic_amd64.deb
    - source: salt://wkhtmltox/files/wkhtmltox_0.12.5-1.bionic_amd64.deb

wkhtmltox:
  cmd.run:
    - name: sudo apt install /tmp/wkhtmltox_0.12.5-1.bionic_amd64.deb -y
    - require:
      - file: /tmp/wkhtmltox_0.12.5-1.bionic_amd64.deb
