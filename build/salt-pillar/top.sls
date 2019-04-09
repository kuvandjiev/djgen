base:
  'G@role:saltstackmaster':
    - match: compound
    - master

  'G@role:djgen':
    - match: compound

  'G@role:djgen and G@environment:dev':
    - match: compound
    - djgen.dev
  
  'G@role:djgen and G@environment:test':
    - match: compound
    - djgen.test

  'G@role:djgen and G@environment:prod':
    - match: compound
    - djgen.prod
