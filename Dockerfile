FROM python:3.11-slim
LABEL org.opencontainers.image.title="Timebook" \
      org.opencontainers.image.description="Simple webapp for tracking how you spend your time." \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/fabiomix/timebook"

# Set environment variables
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ENV FLASK_APP=wsgi.py

# Create a non-root user
RUN groupadd --gid $USER_GID timebook && \
    useradd --uid $USER_UID --gid $USER_GID -m timebook

# Create working and instance folders,
# writable by the non-root user for storing the SQLite database
WORKDIR /app
RUN mkdir -p /app/instance && chown -R timebook:timebook /app/instance

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app
COPY . .

# Image metadata
EXPOSE 8000
VOLUME ["/app/instance"]

# Switch user and run the service
USER timebook
CMD ["gunicorn"]
