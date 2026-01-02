web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
worker: celery -A config.celery_app worker --loglevel=info

