# view-regulations

Example building container with database, data retrieved by API, and UI to view

This uses Docker with Linux, MySQL, Python, and React with JS

## View Regulations

This branch from the original `scratch-web-app` is to accomplish this:

* Pull data from eCFR API
    * https://www.ecfr.gov/developers/documentation/api/v1
* Store data in database
* Process data to show agency regulation count
* Develop UI to show data
* Deploy to public server
* Define potential unique insights
* Implement insights

This app may ignore a containerized solution for speedier development and possibly deployment.

## Containerized Setup

0. Clone this repository first: `git clone git@github.com:EnduringBeta/view-regulations.git`

### Run Docker container

1. Download [Docker Desktop](https://www.docker.com/) and install. Probably sign in. (This program is useful, but following steps will only use the command line functionality.)
2. Inside the repo directory from step 0, run `docker build -t view-regulations .` to build the Docker image
3. Run `docker run -d -p 3306:3306 -p 5000:5000 -p 3000:3000 view-regulations` to start the MySQL and Flask server

These can also be run together via `redocker.sh`

### Test server

4. Go to http://localhost:5000/agencies
5. Add an agency via: `curl -i http://127.0.0.1:5000/agencies -X POST -H 'Content-Type: application/json' -d '{"name":"Wren", "type": "cat"}'`
6. Update an agency via: `curl -i http://127.0.0.1:5000/agencies -X PUT -H 'Content-Type: application/json' -d '{"id": 5, "name":"Sparrow", "type": "cat"}'`
7. Get a single agency via: http://127.0.0.1:5000/agencies/2
8. Remove an agency via: `curl -i http://127.0.0.1:5000/agencies/4 -X DELETE -H 'Content-Type: application/json'`
9. Go to http://localhost:3000

## Local Setup

* Clone the repo
* Create and use Python virtual environment (`python3 -m venv myenv`, `. myenv/bin/activate`)
* Install Python requirements (`pip3 install -r api/requirements.txt`)
* Install Node requirements (`cd ui/ && npm install`)
* Install MySQL (`brew install mysql`)
* Run `./run-app.sh`, which starts the server API (`python3 app.py` and `flask run` also work).

Environment variables may break things; running locally is untested.

On Windows, run `mysqld` to start the database server and `mysqladmin -u root shutdown` to stop it.

### Server Setup

* Copy SSH keys
* Clone the repo
* Create and use Python virtual environment (install venv?)
* Install Python and Node requirements (install npm?)
* Install MySQL (`sudo apt install mysql-server`)
* Start MySQL service and setup to run on boot(`sudo systemctl start mysql; sudo systemctl enable mysql`)
* Set up `run-app-local.sh` to run on boot, or just run?

https://create-react-app.dev/docs/proxying-api-requests-in-development/#configuring-the-proxy-manually

## Troubleshooting

* On Docker run, "Bind for 0.0.0.0:3306 failed: port is already allocated" - stop existing Docker container
* "run-app.sh: Permission denied" - `git update-index --chmod=+x run-app.sh`

* Flask's port 5000 is in use could mean Flask is already running. Use `lsof -i :5000` to find processes and
  kill -9 <process#> to stop it.
* ecfr.gov may block attempts to access resources from new computers. Go to unblock.federalregister.gov to fix this.
* If debugging Flask, run it alone with `flask --app api/app.py run`
* If testing database initialization, it may need to be cleared before being set up again
* Running locally and viewing a droplet maybe can cause port conflicts?

## Tips

* `SELECT user FROM mysql.user;`
* `SHOW DATABASES;`
* `USE mydatabase;`
* `SHOW TABLES;`

## TODO

* Ideally MySQL, Flask, and React are in separate containers
* Enable running locally more easily
* TODOROSS: custom metric, graph, keyword search?
