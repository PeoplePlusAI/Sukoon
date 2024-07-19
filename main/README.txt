To use the Dockerfile:

Place it in the root directory of cloned repo.
Ensure you have a requirements.txt file with all necessary Python dependencies.
Build the Docker image:
docker build -t langgraph-project .

Run the container:
docker run -p 8888:8888 -e OPENAI_API_KEY=your_api_key_here langgraph-project
