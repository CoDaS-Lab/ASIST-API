# CODAS LAB EXPERIMENT

This API is in beta version and part of a game built for ASIST project using FastAPI Web-Framework, Redis and Firebase DB. The API works with the Client available at [ASIST-Client](https://github.com/CoDaS-Lab/ASIST-Client)

## Requirements:
- Redis 6.0.8+ installed
- Python 3.6.4+ installed
- FireBase Realtime Database url and authentication credentials file in json format.

## For Running Locally
- Create a virtual python environment and install python dependencies using `pip install -r requirements.txt`
- Set up the environment variables `REDIS_URL`, `FIREBASE_URL` and `GOOGLE_APPLICATION_CREDENTIALS`. `GOOGLE_APPLICATION_CREDENTIALS` is the path to the json file that contains Firebase database account authentication credentials. 
- Start local redis server `redis-server`
- Start API server `python main.py` and it should be should be available at `http://localhost:5000` 
