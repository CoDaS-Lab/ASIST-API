# CODAS LAB EXPERIMENT

This API is in beta version and part of a game built for ASIST project using FastAPI Web-Framework, Redis and Firebase DB. The API works with the client available at [ASIST-Client](https://github.com/CoDaS-Lab/ASIST-Client)

## Requirements:

- Redis 6.2.5+
- Python 3.9.7+
- [FireBase realtime database URL](https://firebase.google.com/docs/database/rest/start#create_a_database)
- [GOOGLE_APPLICATION_CREDENTIAL](https://firebase.google.com/docs/admin/setup#initialize-sdk)

## Running on localhost

1. Create and activate a virtual python environment.
   - `conda create --name env_name`
   - `conda activate env_name`
2. Install python dependencies.
     - `pip install -r requirements.txt`
3. Setup environment variables
   - `FIREBASE_URL`: Firebase db url path
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to the json file that contains firebase database account authentication credentials.
4. Start Redis server
   - `redis-server`
5. Start API server and it should be should be available at `http://localhost:5000`
   - `python main local.py`
