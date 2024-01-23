from furhat_remote_api import FurhatRemoteAPI
from helpers import *
from intent.intentHelpers import get_query_params, getIntent, return_restaurants
from queries import *
from triples.triple import extract_triples1, triple_embedding, metadata_embedding
from triples.triple_extraction import *
from question import *
from os import system



### helper functions & variables
RUN_WITH_MEMORY = True
conversation_sessions = ['only_short_term', 'short_and_long_term']

# have furhat respond to the query
def respond(response):
    print('\n\nResponding...\n\n')
    print(response)
    furhat.say(text=response, blocking=True)

def contextFromMemory(context, user_input, cm):
    extracted_triple = extract_triples1(user_input, cm.chat, cm.analyzer)
    print(extracted_triple)
    if extracted_triple != []:
        triple = extracted_triple[0]['triple']
        metadata = extracted_triple[0]['meta-data']
        vectorized_metadata = vectorize_meta_data(metadata)

        print(f'Triple: {triple}')
        print(f'Metadata: {metadata}')

        # extract relevant information from the user's memory
        extracted_grand_context = graph_extraction(cm.graph_memory, user_input)
        if extracted_grand_context != "memory empty":
            context['grand_context'] = extracted_grand_context
        extracted_sub_context = vectorized_meta_data_extraction(cm.meta_memory, vectorized_metadata)
        if extracted_sub_context != "memory empty":
            context['sub_context'] = extracted_sub_context

        cm.add_graph_memory(triple)
        cm.add_meta_memory(vectorized_metadata)

        return context


### FURHAT SETUP
# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")

# Set the voice of the robot
furhat.set_voice(name='Matthew')

# Attend a specific location (x,y,z)
furhat.attend(location="0.0,0.2,1.0")

cm = contextualMemory('Furhat', 'User')
isQ = IsQuestion()

print("Press ENTER to start...")
input()

for session in conversation_sessions:
    # Say "Hi there!"
    print('STARTING CONVO...\n\n')
    furhat.say(blocking=True, text="Hi there! How are you {}?".format("feeling" if RUN_WITH_MEMORY else "doing"))


    while True:
        # Perform a named gesture
        furhat.gesture(name="BrowRaise")

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
                        2.67
                    ],
                    "params": {
                        "reset": True
                    }
                }
            ],
            "class": "furhatos.gestures.Gesture"
        })

        # Listen to user speech and return ASR result; wait for 10 seconds
        # system('afplay /System/Library/Sounds/Glass.aiff')
        print("Listening...")
        result = furhat.listen()

        # Check if user said "bye" to break the loop
        # TODO - make sure message ends with "bye"
        if len(set(["bye", "goodbye", "good-bye"]).intersection(set(result.message.lower().split()))) > 0:
            furhat.say(text="Goodbye!", blocking=True)
            break

        ###
        ###
        ### CONVERSATIONAL PIPELINE HERE
        ###
        ###
        user_input = result.message
        print(f'User Input: {user_input}')
        if user_input == '':
            # furhat.say(text="Sorry, did you say something?", blocking=True)
            continue
        intent = getIntent(user_input)
        print(f'Intent: {intent}')
        knowledge_base_info = None
        context = {}

        # check if if intent is within the scope of the agent
        if intent in RELEVANT_INTENTS:
            print(f'Intent is relevant')
            if RUN_WITH_MEMORY and isQ.predict_question(user_input) == 0:
                context = contextFromMemory(context, user_input, cm)
            knowledge_base_info = return_restaurants(get_query_params(user_input))
            context['knowledge_base_info'] = ", ".join(knowledge_base_info)
            print(f'Context: {context}')
            query = gen_restaurant_finder_query(context)
            response = ask_GPT(query)
            respond(response)

        # the intent is not within the scope of the agent
        else:
            # check if the utterance is a question or statement
            if isQ.predict_question(user_input) == 1:
                print('a')
                if intent == 'oos':
                    print('b')
                    intent_string = intent.replace('_', ' ')
                    respond("Sorry, as a restaurant booking agent I cannot answer specific questions about {}.".format(intent_string))
                else:
                    print('c')
                    response = ask_GPT(user_input)
                    respond(response)
            else:
                # add the user's input to the memory as a new episode
                print('d')
                if RUN_WITH_MEMORY:
                    print('e')
                    context = contextFromMemory(context, user_input, cm)
                    print("context: ", context)
                    if context == None:
                        context = {}
                        context['knowledge_base_info'] = "No context"
                query = gen_contextual_query(context, user_input) if RUN_WITH_MEMORY else user_input
                print('g')
                response = ask_GPT(query)
                respond(response)

    ### TODO - COMPILE LONG TERM MEMORY

# Set the LED lights
furhat.set_led(red=0, green=0, blue=0)