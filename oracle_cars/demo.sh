# Run this sh to automatically set up a dev environment for an api demo

# build the image
echo "Building car-api image"
docker build -t car-api:latest .

# ensure temp dir exists. This isn't necessary but will persist data across runs.
echo "Making api db persistence directory"
mkdir /tmp/car_db

# start a new docker network
echo "Creating docker network"
docker network create --driver bridge car-net

# start mysql image
echo "Starting car database container"
docker run --name car-db -p 3306:3306 -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=api_db -v /tmp/car_db:/var/lib/mysql -d --network car-net mysql

# Give the db some time to be properly up and running
sleep 5

# start django image
echo "Starting car api container"
docker run --name car-api -p 8000:8000 --network car-net \
  --env API_DB_USER=root --env API_DB_PASSWORD=secret \
  --env API_DB_HOST=car-db --env API_DB_PORT=3306
  --end CAR_API_DEPLOYMENT=PROD -d car-api:latest


# Give the api some time to be properly up and running
sleep 5

# run db migrations via the django image to make sure our db is set up properly
docker exec car-api python manage.py migrate
docker exec car-api python manage.py spectacular --color --file schema.json
# notify everything is ready
echo "Dev API is ready to use"