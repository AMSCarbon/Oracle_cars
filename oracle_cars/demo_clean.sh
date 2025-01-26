# clean up after running the demo
docker stop car-db car-api
docker container rm car-db car-api
docker network rm car-net
docker image rm car-api
rm -rf /tmp/car_db/