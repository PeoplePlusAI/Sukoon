# !pip install textgrad
import textgrad as tg
import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())
# os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

model = "gpt-4o" # gpt-3.5-turbo
tg.set_backward_engine(model, override=True)

# Step 1: Get an initial response from an LLM.
'''
Initialize the LLM module.
:param engine: The language model engine to use.
:type engine: EngineLM
:param system_prompt: The system prompt variable, defaults to None.
:type system_prompt: Variable, optional
'''

import os

# prompts_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "prompts.txt")
with open("../prompts/prompts.txt", "r") as f:
    system_prompt = f.read()

model = tg.BlackboxLLM(engine="gpt-4o-mini", system_prompt = system_prompt) # , system_prompt = "You are Sukoon..."
question_string = "I've been feeling really down lately and I don't know why. Nothing seems to make me happy anymore."

question = tg.Variable(value = question_string,
                       role_description="user input question describing his mental health issue", #question to the LLM
                       requires_grad=False)

answer = model(question)

print(answer.value)

# answer.value = "I'm sorry to hear that you've been feeling down. It's not uncommon to experience periods of low mood, and it can be frustrating when you can't pinpoint the reason. Have you noticed any changes in your daily routine or any recent stressful events? Sometimes, talking to a mental health professional can help you explore these feelings and find ways to cope. Would you like to discuss some simple self-care strategies that might help lift your mood?"

# updating the answer
answer.set_role_description("emphathetic and helpful answer to the question")

# Step 2: Define the loss function and the optimizer, just like in PyTorch!
# Here, just like SGD, we have TGD (Textual Gradient Descent) that works with "textual gradients".
optimizer = tg.TGD(parameters=[answer]) #optimizer_system_prompt: str = OPTIMIZER_SYSTEM_PROMPT, in_context_examples: List[str] = None
# Methods- zero_grad(): Clears the gradients of all parameters. & step(): Performs a single optimization step.
evaluation_instruction = (f"Here's a question: {question_string}. "
                           "Evaluate the given answer to this question, " #be smart, logical, and very critical
                           "Provide a crisp feedback within 30 words &"
                           "suggest areas for improvement") # identify strengths, areas for improvement, and suggest followup questions

# TextLoss is a natural-language specified loss function that describes
# how we want to evaluate the reasoning.
loss_fn = tg.TextLoss(evaluation_instruction)

loss = loss_fn(answer)

print("\n", loss.value, "\n")

# Step 3: Do the loss computation, backward pass, and update the punchline.
# Exact same syntax as PyTorch!
# loss = loss_fn(answer)
loss.backward() # main step where textual loss gradient propogates backward
optimizer.step() # correction in answer

updated_answer = answer
print(f"\n\n The updated answer is {updated_answer}")