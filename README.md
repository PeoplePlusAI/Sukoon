
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

### Documentation:
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

## How we are using Autogen?

_please see this technical architecture doc for more details - https://www.figma.com/board/ZxX5XSxZDyxYJCFHBI9m6S/Process-Flow?node-id=4974-451&t=RfyoSQeC79Cv7XLI-1 

### Key Components

1. **Autogen Library**: We use Autogen to create and manage multiple AI agents, each with specific roles in the mental health support process.

2. **Chainlit**: Provides the frontend for user interaction, rendering the chat interface and handling user inputs.

3. **RAG (Retrieval-Augmented Generation)**: Implemented to provide agents with access to relevant mental health information using llama index.

### Agent Structure

The system consists of several specialized agents:

1. **ChainlitUserProxyAgent (User)**: 
   - Represents the human user in the system.
   - Configured to always require human input.
   - Limits automatic replies to prevent overwhelming the user.

2. **ChainlitAssistantAgent (PlannerAgent)**:
   - Acts as the central coordinator.
   - Assesses the situation and decides which specialized agent should respond.

3. **ChainlitAssistantAgent (EmpatheticAgent)**:
   - Provides empathetic responses and emotional support.

4. **ChainlitAssistantAgent (SuicidePreventionAgent)**:
   - Specialized in handling crisis situations and suicide prevention.

5. **ChainlitAssistantAgent (RolePlayingAgent)**:
   - Engages in role-playing scenarios to help users practice interactions.

Each agent is initialized with a specific system message (prompt) that defines its role and behavior. The `llm_config` parameter sets the language model configuration for each agent.

### RAG Integration

All assistant agents are equipped with a RAG function, allowing them to retrieve relevant mental health information. This is implemented using:

```python
for agent in [planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent]:
    agent.register_for_llm(
        description="Retrieve content related to mental health topics using RAG.",
        api_style="function"
    )(rag)
```

### Group Chat and Manager

The agents are organized into a group chat:

```python
groupchat = autogen.GroupChat(
    agents=[user_proxy, planner_agent, empathetic_agent, suicide_prevention_agent, role_playing_agent],
    messages=[],
    max_round=15,
    speaker_selection_method="auto",
)

manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
```

The `GroupChat` sets up the interaction between agents, while the `GroupChatManager` oversees the conversation flow.

### Conversation Flow

1. User input is received through the Chainlit interface.
2. The input is passed to the UserProxyAgent.
3. The GroupChatManager directs the conversation to the PlannerAgent.
4. The PlannerAgent assesses the situation and decides which specialized agent should respond.
5. The chosen agent (Empathetic, SuicidePrevention, or RolePlaying) generates a response, potentially using the RAG function for additional information.
6. The response is sent back through the Chainlit interface to the user.

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

Please read the full doc and feel free to add comments here - https://docs.google.com/document/d/1H8-oJmMy0r28kYup9vqt8VGDlY_cCFW_2M07XJxWpFU/edit?usp=sharing 


### Please see this FAQ for common errors - 

https://microsoft.github.io/autogen/docs/FAQ/#handle-rate-limit-error-and-timeout-error
