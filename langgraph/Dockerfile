# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    graphviz \
    libgraphviz-dev \
    pkg-config \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Jupyter
RUN pip install --no-cache-dir jupyter

# Copy the entire project into the container
COPY . .

# Expose port 8888 for Jupyter Notebook
EXPOSE 8888

# Set environment variable for OpenAI API key
# In production, we'll use secrets management instead of hardcoding
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]