# SluggoAPI
Rewrite of cse183 assignment

## Installation

`python3 -m venv sluggoAPI`

For mac / linux:
`source ./sluggoAPI/bin/activate'

For windows:
`.\sluggoAPI\bin\activate.bat`

`pip install -r ./requirements.txt`

Prereq:
Set an environment variable `SLUGGO_DJANGO_KEY` to some random, unique value (only important for production). 
`export SLUGGO_DJANGO_KEY="not important for non producton"`

## To run the program:

Activate the environment

For mac / linux:
`source ./sluggoAPI/bin/activate'

For windows:
`.\sluggoAPI\bin\activate.bat`

Initial run / whenver you make database changes:
`python manage.py makemigrations; python manage.py migrate`

Run with:
`python manage.py runserver`


## Generating Documentation

The documentation engine relies on a schema file. To generate do `python manage.py generateschema > schema.yml`.
