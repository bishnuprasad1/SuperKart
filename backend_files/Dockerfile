# Base image with Python 3.11
FROM python:3.11-slim

# Setting the working directory inside the container
WORKDIR /app

# Copying and installing dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the application code and the serialized model into the container
COPY app.py .
COPY superkart_model.joblib .

# Exposing the port the Flask app listens on
EXPOSE 8000

# Starting the API using gunicorn (a production-grade WSGI server) instead of Flask's dev server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:superkart_api"]
