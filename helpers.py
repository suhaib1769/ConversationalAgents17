from openai import OpenAI
import os

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_KEY"),
)

### helper functions & variables
RELEVANT_INTENTS = ['meal_suggestion', 'restaurant_suggestion', 'travel_suggestion']


#send the query to GPT API and get the response
def ask_GPT(query):

    print("\n\nQUERY FED TO GPT:\n{}\n\n".format(query))

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
        stream=True,
    )

    response_content = ""  # Initialize an empty string to accumulate the response

    for chunk in stream:
        # Concatenate each chunk of content to the response_content variable
        response_content += chunk.choices[0].delta.content or ""

    # TODO - REMOVE 150 CHAR CAP
    return response_content[:150]  # Return the accumulated response content


# create an episode from user memory
def add_to_memory(user_input):
    pass

def extract_from_short_term(user_input):
    pass

def extract_from_long_term(user_input):
    pass