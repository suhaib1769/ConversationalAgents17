### helper functions & variables
RELEVANT_INTENTS = ['meal_suggestion', 'restaurant_suggestion', 'travel_suggestion']


# generate a query from the context to be passed to the LLM
def gen_query(context, user_input):
    
    query = """You are talking to a user. Here is some context about the user for your response:
    {}
    
    Given the context, give a response to the following prompt in one line: {}"""
    context_string = "\n".join([f'"{str(value)}"' for value in context.values()])

    return query.format(context_string, user_input)


# send the query to GPT API and get a response
def ask_GPT(query):
    pass

# create an episode from user memory
def add_to_memory(user_input):
    pass

def extract_from_short_term(user_input):
    pass

def extract_from_long_term(user_input):
    pass