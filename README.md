# SluggoAPI
Rewrite of cse183 assignment

## Installation

`conda env create -f ./sluggo.yml`

`conda activate sluggo`

`pip install -r ./requirements.txt`

This repository takes use of an evironment variable `SLUGGO_DJANGO_KEY` that will be stored with conda, to get access to that please contact someone.

To run the program:

On first time setup, run the command `python manage.py migrate` to set all of the database tables correctly. This command will need to be ran in addition with `python manage.py makemigrations` everytime a new database table is created or a field is edited in a table.

After every pull request merged, make sure to run `python manage.py makemigrations` and `python manage.py migrate` to get any new tables that are necessary. Migrations and the database table are automatically gitignored, so you will not be able to run the program without doing this.

After that, to run the django server do `python manage.py runserver` and navigate to `localhost:8000`