from furhat_remote_api import FurhatRemoteAPI
from questionModule import preprocess_question
from triples.triple import extract_triples1, triple_embedding, metadata_embedding


### helper functions
# send the query to GPT API
def ask_GPT(query):
    pass

# have furhat respond to the query
def respond(response):
    furhat.say(response)

# create an episode from user memory
def add_to_memory(user_input):
    pass



# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")

# Set the voice of the robot
furhat.set_voice(name='Matthew')

# Attend a specific location (x,y,z)
furhat.attend(location="0.0,0.2,1.0")

# furhat.say(text="Hello, my name is Anita!")

while True:
    # Say "Hi there!"
    furhat.say(text="Hi there!")

    # Listen to user speech and return ASR result; wait for 10 seconds
    result = furhat.listen()
    triples = extract_triples1(result.message)
    triple_embeddings = triple_embedding(triples)
    meta_data = metadata_embedding(triples)

    print(triples)
    print(triple_embeddings)
    print(meta_data)


    # Check if user said "bye" to break the loop
    # TODO - make sure message ends with "bye"
    if result.message.lower() == "bye":
        furhat.say(text="Goodbye!")
        break

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

    ### CONVERSATIONAL PIPELINE HERE
    user_input = result.message
    intent = None
    response = None

    # check if the utterance is a question or statement
    if '?' in user_input:
        if intent == 'oos':
            intent_string = intent.replace('_', ' ')
            respond("Sorry, as a restaurant booking agent I cannot answer specific questions about {}.".format(intent_string))
        else:
            ask_GPT(user_input)
    else:
        add_to_memory(user_input)
        # TODO - personalized response pipeline

    # Perform a named gesture
    furhat.gesture(name="BrowRaise")

    # Get the users detected by the robot 
    users = furhat.get_users()

    # Attend the user closest to the robot
    furhat.attend(user="CLOSEST")

    # Set the LED lights
    furhat.set_led(red=200, green=50, blue=50)


# Set the LED lights
furhat.set_led(red=0, green=0, blue=0)