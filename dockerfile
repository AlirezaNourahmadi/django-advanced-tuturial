FROM python:3.8-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN pip3 install "Cython<3"
RUN pip3 install --no-build-isolation -r requirements.txt


COPY ./core /app

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
