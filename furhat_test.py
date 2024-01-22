from furhat_remote_api import FurhatRemoteAPI
from helpers import ask_GPT

# have furhat respond to the query
def respond(response):
    furhat.say(text=response, blocking=True)


### FURHAT SETUP
# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")

# Set the voice of the robot
furhat.set_voice(name='Matthew')

# Attend a specific location (x,y,z)
furhat.attend(location="0.0,0.2,1.0")


# Say "Hi there!"
furhat.say(blocking=True, text="Hi there! How are you doing?")


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
    print("Listening...")
    result = furhat.listen()

    # print the message
    print(result.message)
    user_input = result.message

    # Check if user said "bye" to break the loop
    # TODO - make sure message ends with "bye"
    if len(set(["bye", "goodbye"]).intersection(set(result.message.lower().split()))) > 0:
        furhat.say(text="Goodbye!")
        break


    response = ask_GPT(user_input)
    respond(response)