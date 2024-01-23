# generate a query from the context to be passed to the LLM
def gen_contextual_query(context, user_input):
    
    query = """You are talking to a user. Here is some context about the user for your response:
    {}
    
    Given the context, give a response to the following prompt in one line: {}"""
    context_string = "\n".join([f'"{str(value)}"' for value in context.values()])

    res = query.format(context_string, user_input)
    print(f'Generated query: {res}')
    return res


# generate a query from the context to be passed to the LLM
def gen_restaurant_finder_query(context, user_input):
    
    query = f"""
    You are a restaurant booking agent who speaks with the human, so format the answer as if it is oral, not written. Here are three restaurants the user could like: Restaurant with name: {context['knowledge_base_info']}

    Price ranges range from 1-4, with 1 being lowest and 4 being highest. The best rating possible is a 5. Speak them nicely to the user so they can make an informed choice. Offer to book them a spot in one of the restaurants."""

    print(f'Generated query: {query}')
    return query


# generate a query from the context to be passed to the LLM
def gen_restaurant_booker_query(context, user_input):
    
    query = """You are talking to a user. Here is some context about the user for your response:
    {}
    
    Given the context, give a response to the following prompt in one line: {}"""
    context_string = "\n".join([f'"{str(value)}"' for value in context.values()])

    res = query.format(context_string, user_input)
    print(f'Generated query: {res}')
    return res


# generate a query from the context to be passed to the LLM
def gen_reservation_confirmation_query(context, user_input):
    
    query = """You are talking to a user. Here is some context about the user for your response:
    {}
    
    Given the context, give a response to the following prompt in one line: {}"""
    context_string = "\n".join([f'"{str(value)}"' for value in context.values()])

    res = query.format(context_string, user_input)
    print(f'Generated query: {res}')
    return res