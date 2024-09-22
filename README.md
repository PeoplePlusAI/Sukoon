# Project Sukoon: Mental-Health-Support-using-AI

# Vision
We want to build open-source solutions and standards for using AI to solve mental health challenges. The goal is to apply DPI knowledge and practices that can help professionals deeply explore and understand the latest advancements in AI and how they can be applied to use-cases in mental health specific to India. 


Hey, Welcome to contributing to this open source project to solve Mental health.

# Steps to run

```
- Go to autogen subfolder ( cd autogen) from terminal of your choice
- install all dependencies in your environment (pip install -r requirements.txt)
- run 'python app.py' 
- start talking with AI agents
Note: if you're getting SQL Lite error, please open a git issue.
```

### the previous version used langgraph, for which the steps are:
```
- Go to langgraph subfolder ( cd langgraph) from terminal
- install all dependencies in your environment (pip install -r requirements.txt)
- run 'python sukoon_api.py' 
- go to sukoon-frontend(cd sukoon-frontend), run 'npm start' to access it in your browser.
- alternatively use this vercel deployment to access it - https://sukoon-1.vercel.app
```
Steps to add environment variables - 
```
create a .env file and add these values there -
OPENAI_API_KEY = '<YOUR_OPENAI_API_KEY>' 
LANGCHAIN_API_KEY = '<YOUR_LANGCHAIN_API_KEY>'

- Alternatively , try this:
On Mac/Linux -
export OPENAI_API_KEY=your_api_key_here

On Windows -
setx OPENAI_API_KEY "your_api_key_here"
```


# Progress:
```
We first tried crew ai agent framework which worked well for prototype. (see - https://www.crewai.com/)
We then tried langgraph framework as this was proven to be more robust in production. Both its backend and frontend are built.  (see - https://www.langchain.com/langgraph)
After consulting Bharath(who has worked on AI agents earlier), we decided to shift to Autogen framework. (see - https://microsoft.github.io/autogen/docs/tutorial/introduction/)
However we’re having issues with its web UI ( see github chainlit issues, ors). Also it’s having agent loop issues. 
As next steps, we’ll try to create API endpoints for langgraph (which we had built earlier) and then integrate with whatsapp API. 
For user testing now, we’re using Gooey.ai (which is following exact logic for user flow as used in Autogen and Langgraph) & doing prompt iteration.
```

# Current Landscape
Currently availing mental health has a lot of issues such as:
Stigma -  In India, mental health issues are not considered as healthcare issues. Any person suffering from mental issues is considered weak. Stigma and discrimination often undermine social support structures. Persons suffering from such issues are often tagged as ‘lunatics’ by society. This leads to a vicious cycle of shame, suffering and isolation of the patients.
Lack of awareness - leading to issues like undetected issues and self diagnosis
Availability of trained Mental Healthcare Personnel: There is a severe shortage of mental healthcare workforce in India. According to the WHO, in 2011, there were 0.301 psychiatrists and 0.047 psychologists for every 100,000 patients suffering from a mental health disorder in India. In contrast, the ratio in most developed countries is in excess of 10.
Affordability - Most Mental healthcare sessions are costly as per Indian incomes, hence out of reach of most population(~95%)
Budgetary Constraints - Low budget Allocation: Developed countries allocate 5-18% of their annual healthcare budget on mental healthcare, while India allocates roughly 0.05% (Organization for Economic Co-operation and Development, 2014) of its healthcare budget. This is the lowest among all G20 countries. Despite a rise in mental illness issues, the Union Ministry of Health allocated less than 1% of its budget to directly deal with psychological illnesses in 2022.

# Proposed Solution:
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
