# Car Scheduling API 

## Overview 
A basic API for booking cars based on Django. 

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

## Things I would've liked to add. 

#Schedule endpoints to reflect events. 
I imagine the branch would have some UI the employees could use to confirm when the cars
are picked up and dropped off. We could modify the schedule model with:
```

- branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

+ home_branch = models.ForeignKey(Branch, on_delete=models.CASCADE) 
+ current_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, blank=True, null=True) 
+ real_start = models.DateTimeField()
+ real_end = models.DateTimeField()
```

Then add a couple end points:
```
schedules/<ID>/start
Set the real_start value to show the schedule is underway, set current_branch to null.
schedules/<ID>/finish 
Set the real_end value to show the schedule has finished, set current_branch to the destination.
```

This would make it easier to determine which schedules were actually done, in turn making inventory tracking easier. 
Branches could use the data to determine if users generally go over or under the allotted time, 
#Assign new car on delete
Currently, when a car is deleted any schedule it's in also gets deleted. 
We should instead try to automatically find another car to fulfil the schedule.
We could email the user/customer to notify them about the change, or notify them
that the schedule can no longer be fulfilled. 

#Checking the next schedule's branch when determining availability.
If a car is scheduled for some branch A which is 3 hours away from branch B, 
any new schedule that ends in branch B must end at least 3 hours before the next 
schedule in branch A, such that the car can be relocated. 
We could also consider reassigning a car that's already available at the other branch. 
