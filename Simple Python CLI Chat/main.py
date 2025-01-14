# Implement the Python code using the `openai` library to create the assistant.
# Start with a system prompt for the chat completion API.
# Send a static message and receive a response from the API.
# Show the chat completion message.
from openai import OpenAI

#models for the cost
MODEL_4_MINI = "gpt-4o-mini"

#models we use
MODELS = {
    MODEL_4_MINI: {"input_cost": 0.01 / 1000, "output_cost": 0.03 / 1000},
}
#read API key from .env file
with open('.env', 'r') as fp:
    OPEN_AI_API_KEY = fp.read().strip()


#call to Open AI API and get response
def get_chat_completion(messages,tools=None, tool_choice="auto"):
    client = OpenAI(api_key=f"{OPEN_AI_API_KEY}")
    return client.chat.completions.create(
    model = "gpt-4o-mini",
    messages = messages,
    temperature = 0.5,
    tools = tools,
    max_completion_tokens=100,
    tool_choice = tool_choice,
    )

def response_cost_get(gpt_response_,chat_completion_):
    print(f"Assistant: {gpt_response_}")
    amount = calculate_tokens_cost(MODEL_4_MINI, chat_completion_)
    print(f"Cost: ${amount}")

#tokens cost calculation function
def calculate_tokens_cost(model, chat_completion):
    if model not in MODELS:
        raise ValueError(f"Model {model} is not supported.")

    model_costs = MODELS[model]
    input_tokens_cost = chat_completion.usage.prompt_tokens * model_costs["input_cost"]
    output_tokens_cost = (
        chat_completion.usage.completion_tokens * model_costs["output_cost"]
    )
    return input_tokens_cost + output_tokens_cost

# function calling block
def end_conversation(chat_completion_):
    return chat_completion_

functions_list = [{
    "type":"function",
    "function":{
        "name":"end_conversation",
        "description":"End conversation and print {chat_completion.id}",
        "parameters":{
            "type":"object",
            "properties":{
                "id":{"type":"string","description":"Chat completion"}
            },
            "required":["chat_completion"],
        },
    },
}]

#main function
while True:
    user_input = input("Enter a message:")
    print(f"You: {user_input}")
    messages = [{"role":"system",
                 "content":"You are an helpful assistant for a simple CLI chat. Only respond with text messages. Get creative with the answers!"},
                {"role":"user","content":user_input}]
    chat_completion = get_chat_completion(messages,tools=functions_list)
    gpt_response = chat_completion.choices[0].message.content
    try:
        print(chat_completion.choices[0].message.tool_calls[0].id)
        response_cost_get(gpt_response, chat_completion)
        break
    except:
        pass
    response_cost_get(gpt_response, chat_completion)



