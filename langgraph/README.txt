# Steps to run this - 
- install all dependencies in your environment (pip install -r requirements.txt)
- run 'python sukoon_api_1.py' after that
- go to sukoon-frontend(cd sukoon-frontend), run 'npm start' to access it in your browser.
- alternatively use this vercel deployment to access it - https://sukoon-1.vercel.app


# To use the Dockerfile:

Place it in the root directory of cloned repo.
Ensure you have a requirements.txt file with all necessary Python dependencies.
Build the Docker image:
docker build -t langgraph .

Run the container:
docker run -p 8888:8888 -e OPENAI_API_KEY=your_api_key_here langgraph
