# Use the slim base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of your project files
COPY . /app/

# Expose the port that the application listens on.
EXPOSE 8000

# Command to run the application
CMD python src/db_creator.py && \
    pytest && \
    uvicorn src.agent:app --host 0.0.0.0 --port 8000 --reload

