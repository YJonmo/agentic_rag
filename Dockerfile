# Use NVIDIA's official PyTorch image as the base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy your requirements file (if applicable)
COPY requirements.txt /app/

# add the API keys
ENV NVIDIA_API_KEY="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"
ENV LANGSMITH_API_KEY="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"

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
# CMD ["pytest"]
# CMD ["uvicorn", "src.agent:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# To run in interactive mode use:
# docker run -it --rm -p 8000:8000 agentic_rag /bin/bash

# in command line run
# docker build -t agentic_rag .
# docker run -p 8000:8000 agentic_rag 