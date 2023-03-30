FROM python:3

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

ENV FLASK_APP=app.py

ENV FLASK_APP=0.0.0.0

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . /app

CMD [ "python", "./app.py" ]