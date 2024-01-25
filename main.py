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
        extracted_grand_context = graph_extraction2(cm.graph_memory, user_input)
        if extracted_grand_context != "memory empty":
            context['grand_context'] = extracted_grand_context
        extracted_sub_context = vectorized_meta_data_extraction(cm.meta_memory, vectorized_metadata)
        if extracted_sub_context != "memory empty":
            context['sub_context'] = extracted_sub_context

        cm.add_graph_memory(triple)
        cm.add_meta_memory(vectorized_metadata)

        print(f'Context: {context}')

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


for session in conversation_sessions:

    # allow user to start session
    print("Press ENTER to start...")
    input()

    # Say "Hi there!"
    print('STARTING CONVO...\n\n')
    furhat.say(blocking=True, text="Hi there! How are you {}?".format("feeling" if RUN_WITH_MEMORY else "doing"))
    # furhat.say(blocking=True, text="""
    #            I'm a restaurant booking agent. I can help you find a restaurant and make a reservation. 
    #            You can give me some of the following information such as the city or cuisine. 
    #            Even the name of the restaurant! And if I know it, I can try and provide some information about it for you. 
    #            You can also ask me questions about the restaurant, such as 'Is it expensive?' or 'Is it kid friendly?
    #            Remember, I may or may not be able to remember information you give me, so give me information about yourself and I'll try to remember it.
    #            At the end you can simply say 'bye' to exit the conversation.
    #            Remember to speak only after you hear the ring!
    #            So, what can I do for you?""")

    while True:
        # Listen to user speech and return ASR result; wait for 10 seconds
        system('afplay /System/Library/Sounds/Glass.aiff')
        print("Listening...")
        result = furhat.listen()

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
        print('\nSTOPPED Listening\n\n')
        furhat.listen_stop()

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
        query = ''

        # check if if intent is within the scope of the agent
        if intent in RELEVANT_INTENTS:
            print(f'Intent is relevant')
            if RUN_WITH_MEMORY and isQ.predict_question(user_input) == 0:
                context = contextFromMemory(context, user_input, cm)
                if context == None:
                    context = {}
                    context['knowledge_base_info'] = "No context"

            knowledge_base_info = return_restaurants(get_query_params(user_input))
            print(f'restaurants: {knowledge_base_info}')
            context['knowledge_base_info'] = ", ".join(knowledge_base_info)
            print(f'Context: {context}')

            if intent in ['restaurant_reservation', 'accept_reservation']:
                query = gen_restaurant_booker_query(context, user_input)
                response = ask_GPT(query)
                respond(response)

                # Listen to user speech and return ASR result; wait for 10 seconds
                system('afplay /System/Library/Sounds/Glass.aiff')
                print("Listening...")
                result = furhat.listen()
                user_input = result.message

                query = gen_reservation_query(user_input=user_input)

            elif intent in ['confirm_reservation', 'cancel_reservation']:
                query = gen_reservation_query(user_input=user_input)
            else:
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
                    if RUN_WITH_MEMORY:
                        print('e')
                        context = contextFromMemory(context, user_input, cm)
                        print("context: ", context)
                        if context == None:
                            context = {}
                            context['knowledge_base_info'] = "No context"
                        query = gen_contextual_query(context, user_input) if RUN_WITH_MEMORY else user_input
                    else:
                        query = gen_generic_query(user_input)
                    
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