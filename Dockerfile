FROM python:3.8-slim
ENV FLASK_APP=wsgi.py

# Create working folder
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Run the service
EXPOSE 8000
CMD ["gunicorn"]
