import openai
import os
import time

client = openai.OpenAI(api_key)

# Create a math tutor assistant (you can modify this depending on the assistant's function)
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You have to be conversational. Use the knowledge given by JOHN of situation to answer.",
    tools=[],
    model="gpt-4o",
)

# Start a new conversation thread
thread = client.beta.threads.create()

brain_output = '''
You are a curious and enthusiastic listener whose goal is to help construct a detailed story. For every piece of information the user provides, ask only one thoughtful follow-up question to explore the story in greater depth.
REMAIN PROFESSIONAL AND CONCISE.
For example:
- If the user says 'I killed a man' respond with interest, asking, "Can you tell me more about who this person was?" or "What led up to this event?"
- If the user says "I was fired from my job," follow up with, "What happened before you were fired?"

give reason why u think that dialogue is best
'''

def send_message(thread_id, assistant_id, user_message):
    # User sends a message to the assistant
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message,
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=f"use only johns input to form ur dialogue {brain_output}",
    )

    return run

import json

def save_conversation_to_json(messages):
    conversation_data = []
    
    for i in range(0, len(messages), 2):
        conversation_entry = {}
        if messages[i].role == "user":
            conversation_entry['user'] = messages[i].content[0].text.value
        if i + 1 < len(messages) and messages[i + 1].role == "assistant":
            conversation_entry['assistant'] = messages[i + 1].content[0].text.value
        conversation_data.append(conversation_entry)
    
    with open("conversation.json", "w") as f:
        json.dump(conversation_data, f, indent=4)


def last_message(messages):
    for msg in (messages):
        if msg.role == 'assistant':
            print(f"assistant: {msg.content[0].text.value}")
            break
def real_time_conversation():
    print("You are now conversing with Sukoon. Type 'exit' to quit.")

    while True:
        # Get user input
        user_message = input("You: ")

        if user_message.lower() == "exit":
            print("Ending conversation.")
            break
        
        # Send message and get the response from the assistant
        run = send_message(thread.id, assistant.id, user_message)
        # Once completed, retrieve the messages from the thread
        messages = client.beta.threads.messages.list(thread_id=thread.id).data
        
        last_message(messages)

        save_conversation_to_json(messages)

real_time_conversation()
client.beta.assistants.delete(assistant.id)