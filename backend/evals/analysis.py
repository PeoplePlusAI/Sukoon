import openai
import json
import os  
import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import re
# Load environment variables from .env file
load_dotenv(find_dotenv())

api_key = os.getenv("OPENAI_API_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_CLIENT_ANON_KEY")

client = OpenAI(
    api_key=api_key,
)

def analyze_conversation(user_message, sukoon_response):
    # Construct the prompt for the LLM
    prompt = f"""
            Given the following conversation between a user and a chatbot named 'Sukoon':

            User: "{user_message}"

            Sukoon: "{sukoon_response}"

            Analyze the conversation and provide the analysis in the following JSON format:

            {{
            "user_analysis": {{
                "primary_concern": "<main mental health issue or emotional state>",
                "subject_category": "<choose from: General Greeting, Emotional Support, Mental Health Information, Coping Strategies, Crisis Management, Feedback, or Other>",
                "emotional_tone": "<overall emotional tone of the user's message>"
            }},
            "sukoon_response_evaluation": {{
                "empathy_rating": <rate from 1-5 how well Sukoon demonstrated empathy>,
                "relevance_rating": <rate from 1-5 how relevant Sukoon's response was to the user's concern>,
                "clarity_rating": <rate from 1-5 how clear and easy to understand Sukoon's response was>,
                "helpfulness_rating": <rate from 1-5 how helpful Sukoon's suggestions or information were>,
                "overall_rating": <calculate the average of the above ratings>,
                "strengths": ["<list key strengths of Sukoon's response>"],
                "areas_for_improvement": ["<list areas where Sukoon's response could be improved>"],
                "suggested_follow_up": "<provide a suggestion for how Sukoon could follow up or what question it could ask next>"
            }}
            }}

            Ensure that the output is valid JSON that can be parsed by Python's json.loads() function. Avoid including any markdown formatting like code blocks. Output only the JSON object.
            """

    # Call the OpenAI API to get the analysis
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that analyzes conversations between users and the chatbot 'Sukoon'."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500,
        response_format = { "type": "json_object" }
    )

    # Extract the assistant's reply
    analysis_text = response.choices[0].message.content
    # Attempt to parse the response as JSON
    try:
        # Remove code block formatting if present
        analysis_text = analysis_text.strip()
        if analysis_text.startswith("```"):
            # Use regex to remove code block markers
            analysis_text = re.sub(r'^```(?:json)?\n?', '', analysis_text)
            analysis_text = re.sub(r'\n?```$', '', analysis_text)

        analysis_json = json.loads(analysis_text)

        # Add original messages to the analysis
        analysis_json['user_message'] = user_message
        analysis_json['sukoon_response'] = sukoon_response
    # Attempt to parse the response as JSON
        analysis_json = json.loads(analysis_text)
        return analysis_json
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("LLM Response:", analysis_text)
        return None

# Example usage
if __name__ == "__main__":
    # sample conversation
    # user_message = "I've been feeling really down lately and I don't know why. Nothing seems to make me happy anymore."
    # sukoon_response = "I'm sorry to hear that you've been feeling down. It's not uncommon to experience periods of low mood, and it can be frustrating when you can't pinpoint the reason. Have you noticed any changes in your daily routine or any recent stressful events? Sometimes, talking to a mental health professional can help you explore these feelings and find ways to cope. Would you like to discuss some simple self-care strategies that might help lift your mood?"

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
    }
    # to read all table
    # response = requests.get('https://supabase.pplus.ai/rest/v1/Sukoon Student?select=*', headers=headers)
    # to read specific columns - user_message and Output
    response = requests.get('https://supabase.pplus.ai/rest/v1/Sukoon%20Student?select=user_message,Output', headers=headers)
    
    if response.status_code ==200:
        data = response.json()
        df = pd.DataFrame(data)
    elif response.status_code ==500:
        print("Internal server error")
    else:
        print("Error fetching data:", response.status_code)
        df = pd.DataFrame()
    
    # Convert DataFrame to list of records
    records = df.to_dict('records')

    # List to store all analyses
    analyses = []
    
    # for index, row in df.iterrows():
    for row in records:
        user_message = row.get('user_message', '')
        sukoon_response = row.get('Output', '')
        if not user_message or not sukoon_response:
            continue  # Skip if data is missing
        
        analysis = analyze_conversation(user_message, sukoon_response)
        analysis['user_message'] = user_message
        analysis['sukoon_response'] = sukoon_response
        if analysis:
            analyses.append(analysis)
            print(json.dumps(analysis, indent=2))
        else:
            # Handle cases where analysis failed
            print(f"Analysis failed for conversation with user_message: {user_message}")

        # append all files to one analysis text or somewhere suitable
        with open("data/analysis_data/analysis.json", "w") as file:
            # file.write(f"{json.dumps(analysis)}\n\n")
            json.dump(analyses, file, indent=2)




