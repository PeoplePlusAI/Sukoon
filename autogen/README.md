
# Project Sukoon: Mental-Health-Support-using-AI

# Vision
We want to build open-source solutions and standards for using AI to solve mental health challenges. The goal is to apply DPI knowledge and practices that can help professionals deeply explore and understand the latest advancements in AI and how they can be applied to use-cases in mental health specific to India. 

_This project uses Autogen framework whose link can be found here -  https://github.com/microsoft/autogen_

# Steps to run
```
- Go to autogen subfolder ( cd autogen) from terminal
- install all dependencies in your environment (pip install -r requirements.txt)
- run 'python app.py' or 'mhfa_1.py'
```
Steps to add environment variables - 
```
create a .env file and add these values there -
OPENAI_API_KEY = '<YOUR_OPENAI_API_KEY>' 

- Alternatively , try this:
On Mac/Linux -
export OPENAI_API_KEY=your_api_key_here

On Windows -
setx OPENAI_API_KEY "your_api_key_here"
```

Documentation:
Please see this article to understand how Autogen works - https://microsoft.github.io/autogen/docs/Getting-Started

## Understanding and Debugging AutoGen

## What is AutoGen?

AutoGen is a framework for building multi-agent systems using large language models (LLMs). It allows you to create conversational AI agents that can interact with each other and with humans to solve complex tasks.

Key features:
1. Multi-agent conversations
2. Customizable agent roles and behaviors
3. Integration with external tools and APIs
4. Flexible conversation flow control

## Core Concepts

1. **Agents**: The building blocks of AutoGen. Each agent has a specific role (e.g., user proxy, assistant, coder).

2. **GroupChat**: A conversation environment where multiple agents interact.

3. **GroupChatManager**: Manages the flow of conversation in a GroupChat.

4. **UserProxyAgent**: Represents the human user or serves as an interface for human input.

5. **AssistantAgent**: AI-powered agents that perform tasks or provide information.

## Common Debugging Issues and Solutions

1. **API Key Issues**
   - Problem: "Invalid API key" or "Authentication failed" errors.
   - Solution: Double-check your API key in the `OAI_CONFIG_LIST` file or environment variables.

2. **Infinite Loops**
   - Problem: Agents keep talking to each other without reaching a conclusion.
   - Solution: 
     - Adjust the `max_round` parameter in GroupChat.
     - Implement better termination conditions in agent logic.
     - Use `allow_repeat_speaker=False` in GroupChat to prevent the same agent from speaking consecutively.

3. **Unexpected Agent Behavior**
   - Problem: Agents not following their intended roles or instructions.
   - Solution: 
     - Review and refine the `system_message` for each agent.
     - Use more specific prompts or examples in the agent's instructions.
     - Implement additional logic in custom agent classes to enforce desired behavior.

4. **Memory Issues**
   - Problem: Agents forgetting previous context or information.
   - Solution:
     - Implement a custom memory system for agents.
     - Use the `memory` parameter in agent configuration to specify a memory backend.

5. **Error Handling**
   - Problem: Unhandled exceptions breaking the conversation flow.
   - Solution:
     - Implement try-except blocks in critical sections.
     - Create custom error handling logic in your GroupChatManager subclass.

6. **Performance Issues**
   - Problem: Slow response times or high token usage.
   - Solution:
     - Use more efficient models for less complex tasks.
     - Implement caching mechanisms for frequently accessed information.
     - Optimize prompts to reduce token usage.

7. **Integration Issues**
   - Problem: Difficulty integrating external tools or APIs.
   - Solution:
     - Use the `function_map` parameter in UserProxyAgent to register custom functions.
     - Implement custom agents that handle specific API integrations.

8. **Debugging Tips**
   - Use `print` statements or logging to track conversation flow and agent decisions.
   - Implement a debug mode that provides more verbose output during execution.
   - Use AutoGen's built-in conversation saving features to analyze conversations post-execution.

Remember, AutoGen is highly customizable. Many issues can be resolved by subclassing existing components and implementing custom logic to suit your specific needs.

# Current Landscape
Currently availing mental health has a lot of issues such as:
Stigma -  In India, mental health issues are not considered as healthcare issues. Any person suffering from mental issues is considered weak. Stigma and discrimination often undermine social support structures. Persons suffering from such issues are often tagged as ‘lunatics’ by society. This leads to a vicious cycle of shame, suffering and isolation of the patients.
Lack of awareness - leading to issues like undetected issues and self diagnosis
Availability of trained Mental Healthcare Personnel: There is a severe shortage of mental healthcare workforce in India. According to the WHO, in 2011, there were 0.301 psychiatrists and 0.047 psychologists for every 100,000 patients suffering from a mental health disorder in India. In contrast, the ratio in most developed countries is in excess of 10.
Affordability - Most Mental healthcare sessions are costly as per Indian incomes, hence out of reach of most population(~95%)
Budgetary Constraints - Low budget Allocation: Developed countries allocate 5-18% of their annual healthcare budget on mental healthcare, while India allocates roughly 0.05% (Organization for Economic Co-operation and Development, 2014) of its healthcare budget. This is the lowest among all G20 countries. Despite a rise in mental illness issues, the Union Ministry of Health allocated less than 1% of its budget to directly deal with psychological illnesses in 2022.

# Proposed Solution
AI Companion
Solves for personalization, accessibility (available 24/7), affordability

# Features:
Personalized and contextual responses 
Emotional understanding and support
Privacy-focused, with no central data storage 
Supplemental real healthcare professional support → Escalation features
Multi-user chat interface capabilities with option to invite partner / parent → Shared wellness journey
Cultural Sensitivity in Indian context

# What could a solution look like? (Tentative features) 
Very personal approach with focus on listening and emphasising
Available in 22 Indic regional languages, especially on mobile devices
Stores the user conversation locally, not on cloud -> ensuring complete privacy
Will provide helpful resources for most common mental health problems. However, it'll not prescribe any medicines
For training the bot , we can use federated learning
Will be available as an API, so interested people can try this and build on top of it, based on their use case
Aim is to get national-level adoption
If serious, there’ll option to reach out to a psychiatrist or support community groups e.g. peer to peer network
Have L1/L2/L3 level of support 

# Some interesting ideas to try: 
Can we gamify the whole conversation? If yes, then how? 
Can we nudge users to adopt healthier behaviour? 
In particular, we can warn users about what not to do - relying on superstitions, isolation, labelling, and other unhelpful tactics
Give positive self-affirmation, create safety plan, etc
Can we develop Emotional Intelligence that understands not just emotions, but context behind it
Can we detect emotional status ike stress level using voice(like hume) and then support him
Can we create a timeline tracker let’s say six month plan for meditation and track streak
Can we give them a phone number they can call to? The bot will mainly listen , empathize and offer safe advice

Please read the full doc and feel free to add comments here - https://docs.google.com/document/d/1H8-oJmMy0r28kYup9vqt8VGDlY_cCFW_2M07XJxWpFU/edit?usp=sharing 


### Please see this FAQ for common errors - 

https://microsoft.github.io/autogen/docs/FAQ/#handle-rate-limit-error-and-timeout-error