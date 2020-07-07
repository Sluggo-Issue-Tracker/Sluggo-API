# SluggoAPI
Rewrite of cse183 assignment

## Installation

`conda env create -f ./sluggo.yml`

`pip install -r ./requirements.txt`

This repository takes use of an evironment variable `SLUGGO_DJANGO_KEY`, to get access to that please contact someone.

To run the program:

On first time setup, run the command `python manage.py migrate` to set all of the database tables correctly. This command will need to be ran in addition with `python manage.py makemigrations` everytime a new database table is created or a field is edited in a table.

After that, to run the django server do `python manage.py runserver` and navigate to `localhost:8000`