import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read the template file
with open('OAI_CONFIG_LIST.template.json', 'r') as template_file:
    config_template = json.load(template_file)

# Replace placeholders with actual API key
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

for config in config_template:
    config['api_key'] = api_key

# Write the configuration to OAI_CONFIG_LIST
try:
    with open('OAI_CONFIG_LIST', 'w') as config_file:
        json.dump(config_template, config_file, indent=2)

    print("OAI_CONFIG_LIST file generated successfully.")
    
except:
    print("OAI_CONFIG_LIST already exists")