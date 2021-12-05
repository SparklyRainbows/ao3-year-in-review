web: python server.py
worker: python server.py 
web: gunicorn --bind 0.0.0.0:$PORT flaskapp:app