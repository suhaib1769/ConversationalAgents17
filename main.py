from furhat_remote_api import FurhatRemoteAPI
from helpers import *
from intent.intentHelpers import get_query_params, getIntent, return_restaurants
from triples.triple import extract_triples1, triple_embedding, metadata_embedding



### helper functions & variables
RUN_WITH_MEMORY = False
conversation_sessions = ['only_short_term', 'short_and_long_term']

# have furhat respond to the query
def respond(response):
    furhat.say(text=response)


### FURHAT SETUP
# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")

# Set the voice of the robot
furhat.set_voice(name='Matthew')

# Attend a specific location (x,y,z)
furhat.attend(location="0.0,0.2,1.0")

# furhat.say(text="Hello, my name is Anita!")

for session in conversation_sessions:
    # Say "Hi there!"
    furhat.say(text="Hi there! How are you {}?".format("feeling" if RUN_WITH_MEMORY else "doing"))

    while True:
        # Listen to user speech and return ASR result; wait for 10 seconds
        result = furhat.listen()

        # Check if user said "bye" to break the loop
        # TODO - make sure message ends with "bye"
        if len(set(["bye", "goodbye"]).intersection(set(result.message.lower().split()))) > 0:
            furhat.say(text="Goodbye!")
            break


        triples = extract_triples1(result.message)
        triple_embeddings = triple_embedding(triples)
        meta_data = metadata_embedding(triples)

        print(triples)
        print(triple_embeddings)
        print(meta_data)


        

        # print the message
        print(result.message)
        
        # Perform a custom gesture
        furhat.gesture(body={
            "frames": [
                {
                    "time": [
                        0.33
                    ],
                    "params": {
                        "BLINK_LEFT": 1.0
                    }
                },
                {
                    "time": [
                        0.67
                    ],
                    "params": {
                        "reset": True
                    }
                }
            ],
            "class": "furhatos.gestures.Gesture"
        })


        ###
        ###
        ### CONVERSATIONAL PIPELINE HERE
        ###
        ###
        user_input = result.message
        intent = getIntent(user_input)
        knowledge_base_info = None
        context = {}

        # check if if intent is within the scope of the agent
        if intent in RELEVANT_INTENTS:
            knowledge_base_info = return_restaurants(get_query_params(user_input))
            context['knowledge_base_info'] = knowledge_base_info
            query = gen_query(context, user_input)
            response = ask_GPT(query)
            respond(response)



        # the intent is not within the scope of the agent
        else:

            # check if the utterance is a question or statement
            if '?' in user_input:
                if intent == 'oos':
                    intent_string = intent.replace('_', ' ')
                    respond("Sorry, as a restaurant booking agent I cannot answer specific questions about {}.".format(intent_string))
                else:
                    response = ask_GPT(user_input)
                    respond(response)
            else:
                # add the user's input to the memory as a new episode

                if RUN_WITH_MEMORY:
                    add_to_memory(user_input)

                    # extract relevant information from the user's memory
                    extracted_short_term = extract_from_short_term(user_input)
                    context['short_term_memory'] = extracted_short_term
                    extracted_long_term = extract_from_long_term(user_input)
                    context['long_term_memory'] = extracted_long_term

                query = gen_query(context, user_input) if RUN_WITH_MEMORY else user_input
                response = ask_GPT(query)
                respond(response)

    ### TODO - COMPILE LONG TERM MEMORY





        


# Set the LED lights
furhat.set_led(red=0, green=0, blue=0)