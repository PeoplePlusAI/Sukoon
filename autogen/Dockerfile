# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir pyautogen pyautogen[retrievechat] openai chromadb

# Make port 80 available to the world outside this container
EXPOSE 80

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Run app.py when the container launches
CMD ["python", "app.py"]