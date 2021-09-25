FROM python:3.8.5

RUN mkdir /code

COPY ./backend/requirements.txt /code

RUN pip3 install -r /code/requirements.txt

COPY ./backend /code

WORKDIR /code
 
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
