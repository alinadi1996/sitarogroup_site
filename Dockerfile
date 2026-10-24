FROM python:3.15.0rc3-alpine3.24

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN addgroup app && adduser -S -G app app
USER app



COPY requirements.txt /app/
RUN pip install -r requirements.txt

EXPOSE 8000

COPY . /app/


