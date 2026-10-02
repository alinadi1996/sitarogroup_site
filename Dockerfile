FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/
RUN groupadd --gid 10001 sitaro && useradd --uid 10001 --gid sitaro --no-create-home sitaro \
    && mkdir -p /code/staticfiles /code/media \
    && chown sitaro:sitaro /code/staticfiles /code/media
USER sitaro
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--config", "deploy/gunicorn.conf.py"]

