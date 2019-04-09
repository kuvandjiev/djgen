To initialize the local development environment execute:
 
docker network create --gateway 173.17.2.1 --subnet 173.17.2.0/24 app_djtest_net
docker volume create --name=postgresql-djtest-volume
docker-compose up
