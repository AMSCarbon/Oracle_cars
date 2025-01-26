FROM python:3.10

ENV PORT 8000

WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN mkdir -p /var/www/static
RUN python ./manage.py collectstatic --noinput
RUN cp -r /var/www/static .

CMD gunicorn oracle_cars.wsgi:application

EXPOSE ${PORT}