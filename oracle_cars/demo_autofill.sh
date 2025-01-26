# make a bunch o' post requests to populate data
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"name":"Prague"}' 127.0.0.1:8000/api/branches/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"name":"Brno"}' 127.0.0.1:8000/api/branches/

curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C1000", "branch": "1", "make": "Honda", "model": "Civic"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C1001", "branch": "1", "make": "Honda", "model": "Civic"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C2000", "branch": "1", "make": "Honda", "model": "Accord"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C2001", "branch": "1", "make": "Honda", "model": "Accord"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C3000", "branch": "1", "make": "Ford", "model": "Focus"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C3001", "branch": "1", "make": "Ford", "model": "Focus"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C3002", "branch": "1", "make": "Ford", "model": "Focus"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C4000", "branch": "1", "make": "Ford", "model": "Falcon"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C4001", "branch": "2", "make": "Ford", "model": "Falcon"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C4002", "branch": "2", "make": "Ford", "model": "Falcon"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C5000", "branch": "2", "make": "Ford", "model": "Mustang"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C5001", "branch": "2", "make": "Ford", "model": "Mustang"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C6000", "branch": "2", "make": "Holden", "model": "Barina"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C6001", "branch": "2", "make": "Holden", "model": "Barina"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C7000", "branch": "2", "make": "Holden", "model": "Captiva"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C7001", "branch": "2", "make": "Holden", "model": "Captiva"}' 127.0.0.1:8000/api/cars/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"id":"C7002", "branch": "2",  "make": "Holden", "model": "Captiva"}' 127.0.0.1:8000/api/cars/

curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"start_time":"2025-02-01 08:00:00+00:00",  "duration": "12:00:00", "origin_branch":"1", "destination_branch":"1"}' 127.0.0.1:8000/api/schedules/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"start_time":"2025-02-01 08:00:00+00:00",  "duration": "12:00:00", "origin_branch":"1", "destination_branch":"1"}' 127.0.0.1:8000/api/schedules/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"start_time":"2025-02-01 08:00:00+00:00",  "duration": "72:00:00", "origin_branch":"1", "destination_branch":"2"}' 127.0.0.1:8000/api/schedules/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"start_time":"2025-06-01 08:00:00+00:00",  "duration": "50:00:00", "origin_branch":"1", "destination_branch":"2"}' 127.0.0.1:8000/api/schedules/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"start_time":"2025-09-01 08:00:00+00:00",  "duration": "01:00:00", "origin_branch":"2", "destination_branch":"2"}' 127.0.0.1:8000/api/schedules/
curl -X POST -w "\n" -H 'Content-Type: application/json' -d '{"start_time":"2025-10-01 08:00:00+00:00",  "duration": "00:15:00", "origin_branch":"2", "destination_branch":"2"}' 127.0.0.1:8000/api/schedules/
