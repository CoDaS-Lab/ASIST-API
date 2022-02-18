# Dockerfile

FROM python:3.9.4-slim

WORKDIR /app

# set env variables
ENV REDIS_URL XXXXXXXXXXXXXX
ENV FIREBASE_URL XXXXXXXXXXXXXX
ENV  GOOGLE_APPLICATION_CREDENTIALS. GOOGLE_APPLICATION_CREDENTIALS XXXXXXXXXXXXXX

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .