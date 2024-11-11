# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
# COPY sukoon.py .
# COPY sukoon_api.py .

COPY . .

# Create necessary directories
RUN mkdir -p /app/prompts
RUN mkdir -p /app/storage

# Copy additional configuration files
# COPY prompts.yaml .
# COPY .env .

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8001

# Expose the port
EXPOSE 8001

# Run the FastAPI application
CMD ["uvicorn", "sukoon_api:app", "--host", "0.0.0.0", "--port", "8001"]

# # Use Python 3.9 slim image as base
# FROM python:3.9-slim

# # Set working directory
# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Create project structure
# RUN mkdir -p /app/my_agent/utils

# # Copy requirements first to leverage Docker cache
# COPY my_agent/requirements.txt /app/my_agent/
# RUN pip install --no-cache-dir -r my_agent/requirements.txt

# # Copy project files
# COPY my_agent/__init__.py /app/my_agent/
# COPY my_agent/agent.py /app/my_agent/
# COPY my_agent/utils/ /app/my_agent/utils/
# COPY langgraph.json /app/
# COPY .env /app/

# # Set Python path
# ENV PYTHONPATH=/app

# # Create necessary directories
# RUN mkdir -p /app/prompts
# RUN mkdir -p /app/storage

# # Copy additional configuration files
# COPY prompts/prompts.yaml /app/prompts/

# # Set environment variables
# ENV HOST=0.0.0.0
# ENV PORT=8001

# # Expose the port
# EXPOSE 8001

# # Run the application
# CMD ["python", "-m", "my_agent.agent"]