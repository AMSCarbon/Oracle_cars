# Car Scheduling API 

## Overview 
A basic API for booking cars 

## Quickstart
There are two ways to set up dev environment for this API. 

The first is to use the standard django commands to set up a dev instance. 
```
python ./manage.py migrate # set up the database
python ./manage.py runserver # start the server 
```
The second way is to use the provided demo bash scripts. These scripts set up 
the api and database containers, populate data and clean up once completed.

 - demo.sh: build the django image, then start running the MySQL db and api containers
 - demo_autofill.sh: send a bunch of curl requests to the api to fill in the db.
 - demo_clean.sh: stop the containers and remove resources that were created (except the mysql image)

This may need to be run with sudo depending on how docker permissions are set up on your device.


## Design 

##