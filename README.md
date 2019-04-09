To initialize the local development environment execute:
 
docker network create --gateway 173.17.2.1 --subnet 173.17.2.0/24 app_djtest_net
docker volume create --name=postgresql-djtest-volume
docker-compose up

To provision a new instance execute:

```fab -r build/ provision <instance-name>```

and follow the instructions.

To deploy a new instance execute:

``` fab -r build/ deploy <instance-name>```

and follow the instructions.

Make sure that you can ssh to the instances that you want to provision with the current user.
```ssh <instance-ip>``` must work
