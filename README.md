# Sluggo-API
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Sluggo is a small and flexible issue tracker for small teams, intended
to provide an effective free and (eventually) open source alternative to
tools like JIRA and GitHub Issues, while providing a modern user
experience not typically seen in open source issue trackers.

This repository holds the backend Django application for Sluggo, which
will provide a server which Sluggo frontends may connect to.

## Installation
Currently, installation steps are focused on development. This process
will hopefully be simplified once more complete versions of the tracker
are available.

To install Sluggo on development machines, perform the following:

1. Create the virtual environment for Sluggo using the command
`python3 -m venv sluggoAPI`

2. Activate the Sluggo virtual environment.

    a. For POSIX platforms (macOS
and Linux) run:
`source ./sluggoAPI/bin/activate`

    b. For Windows:
`.\sluggoAPI\Scripts\activate.bat`

3. Install the dependencies for Sluggo to run using the command
`pip install -r ./requirements.txt`

4. Set the environment variable `DJANGO_SECRET_KEY` to some random,
unique value (only important for production):
`export DJANGO_SECRET_KEY="not important for non producton"`

5. If using the Vue frontend, set the `VUE_ROOT` variable to the URL at
which your Vue app is hosted (e.g. `http://localhost:8080`)

6. (optional) Install the pre-commit hook:
`pre-commit install`

## Development Setup
We recommend the following set of environment variables for development:
```
DJANGO_SECRET_KEY=<any value>
JWT_SECRET=<any value>
DEBUG=True
VUE_ROOT=http://localhost:8080/
ALLOWED_HOST=localhost:8080
```

A typical workflow will include development of the API, in addtion to the SPA. In order to
test the app fully, one should configure the `VUE_ROOT` and `ALLOWED_HOST` environment variables
in order to satisfy CSRF requirements. `DJANGO_SECRET_KEY` and `JWT_SECRET` are also required;
*because the development environment is intened to run on one's local machine, these can be arbitrary*.
In production, these values should be configured to be sufficiently long and hard to guess. `DEBUG`
affects where Django serves its static content from.

For developing against a database other than the default, see below.

## Database Setup
Out of the box, Sluggo-API will use a SQLite backend, which may not be
suitable for larger instances. You may also choose to move the SQLite
database to another file. Here are instructions on how to modify the
database config:

### Engines
To set an engine, set the `SLUGGO_DB_ENGINE` environment variable.

Valid engines are
* `sqlite3` - SQLite backend (default)
* `postgresql` - Postgres backend
* `mysql` - MySQL and MariaDB backend
* `oracle` - Oracle backend

There may be some issues with using different database backends. We
are still determining which databases to primarily support.

### Other Options
* `SLUGGO_DB_NAME` - Name of the database on a remote database, or the
path to the SQLite file for the SQLite backend.
* `SLUGGO_DB_HOST` - Remote DB only. Used for specifying the host
address of the remote database.
* `SLUGGO_DB_PORT` - Remote DB only. Used for specifying the port number of
the remote database.
* `SLUGGO_DB_USER` - Remote DB only. Used for specifying the user
to login with on the remote database.
* `SLUGGO_DB_PASS` - Remote DB only. Used for specifying the password for the
user login on the remote database.

### Example Postgres Configuration
An example Postgres configuration is listed below:

```
SLUGGO_DB_ENGINE=postgresql
SLUGGO_DB_NAME=sluggo
SLUGGO_DB_HOST=127.0.0.1
SLUGGO_DB_PORT=5432
SLUGGO_DB_USER=sluggo
SLUGGO_DB_PASS=1234
```


## Initialization

This must be ran the first time. Do the following:

1. Activate the virtual environment shown in the Installation steps.

    a. For POSIX platforms (macOS and Linux):
`source ./sluggoAPI/bin/activate`

    b. For Windows:
`.\sluggoAPI\Scripts\activate.bat`

2. Run the following command whenever changes to the database models
are made. This is likely necessary whenever new versions of the
repository are pulled, or your version of Sluggo-API is otherwise
upgraded:
`python manage.py makemigrations; python manage.py migrate`

3. Create a superuser with the command:
`python3 manage.py createsuperuser`

4. Run with:
`python manage.py runserver`

## Initialization for Slack

This assumes that a slack app is already created. Do the following:

1. Create a superuser with the command:
`python3 manage.py createsuperuser`

2. In a browser navigate to `$HOST/admin`, replacing `$HOST` with whatever the domain the local server is run with.

3. Add a Social Application. (this is not important if you are not dependent on the slack api)

    a. Set provider to Slack

    b. Set name to something appropriate like slack or slack-bot, etc

    c. Enter the Client id from the slack bot's dashboard

    d. Enter the secret key from the slack bot's dashboard

    e. Leave Key empty

    f. Choose the first site in the list (likely to be `example.com`)

    g. Save.

## Running

1. Activate the virtual environment shown in the Installation steps.

    a. For POSIX platforms (macOS and Linux):
`source ./sluggoAPI/bin/activate`

    b. For Windows:
`.\sluggoAPI\Scripts\activate.bat`

2. Run the following command whenever changes to the database models
are made. This is likely necessary whenever new versions of the
repository are pulled, or your version of Sluggo-API is otherwise
upgraded:
`python manage.py migrate`

3. Run with:
`python manage.py runserver`

## Documentation
Documentation is hosted within the browser when you run a copy of the
server, and is automatically updated to the latest changes made to
the API. Additionally, the documentation is interactive, and will let
you immediately experiment with the API and its various endpoints given
input data. For more details, see [SwaggerUI's documentation](https://github.com/swagger-api/swagger-ui).

To launch the documentation server, simply run your Django server by
running `python manage.py runserver` as above.

In your browser, navigate to `$HOST/api/schema/swagger-ui` for a
browsable overview of the endpoints, replacing `$HOST` with the IP and
port on which you are running the API (for example, 127.0.0.1:8000).

## Contributing
Currently, we are not accepting third-party contributions to Sluggo-API.
We are focusing our efforts on developing a solid core application which
can accept more developers. We intend to determine the best way to
approach accepting third party contributions, and will do so when
we feel the project is in a good state to do so.

For internal contributors, please read CONTRIBUTING.md
for guidance on contribution standards.

## License
This project is licensed under the Apache 2.0 license.
