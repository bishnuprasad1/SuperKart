# Base image with Python 3.11
FROM python:3.11-slim

# Setting the working directory inside the container
WORKDIR /app

# Copying and installing dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the Streamlit application code into the container
COPY app.py .

# Exposing the port Streamlit listens on
EXPOSE 8501

# Starting the Streamlit app, bound to all interfaces so it is reachable from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
