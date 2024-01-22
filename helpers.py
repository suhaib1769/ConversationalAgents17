from openai import OpenAI
import os

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_KEY"),
)

### helper functions & variables
RELEVANT_INTENTS = ['meal_suggestion', 'restaurant_suggestion', 'travel_suggestion']


# generate a query from the context to be passed to the LLM
def gen_query(context, user_input):
    
    query = """You are talking to a user. Here is some context about the user for your response:
    {}
    
    Given the context, give a response to the following prompt in one line: {}"""
    context_string = "\n".join([f'"{str(value)}"' for value in context.values()])

    return query.format(context_string, user_input)

#send the query to GPT API and get the response
def ask_GPT(query):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
        stream=True,
    )

    response_content = ""  # Initialize an empty string to accumulate the response

    for chunk in stream:
        # Concatenate each chunk of content to the response_content variable
        response_content += chunk.choices[0].delta.content or ""

    return response_content  # Return the accumulated response content


# create an episode from user memory
def add_to_memory(user_input):
    pass

def extract_from_short_term(user_input):
    pass

def extract_from_long_term(user_input):
    pass