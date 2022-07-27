# Dockerfile for sluggo app
# code lifted from: https://docs.docker.com/samples/django/

# build backend stuff
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt

# run migrations
ENTRYPOINT [ "sh", "./docker-entrypoint.sh" ]
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8080" ]
