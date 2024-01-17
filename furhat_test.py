from furhat_remote_api import FurhatRemoteAPI

# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")

# Set the voice of the robot
furhat.set_voice(name='Matthew')

# Attend a specific location (x,y,z)
furhat.attend(location="0.0,0.2,1.0")

furhat.say(text="Hello, my name is Anita!")

while True:
    # Say "Hi there!"
    # furhat.say(text="Hi there!")

    # Listen to user speech and return ASR result
    result = furhat.listen()

    # print the message
    print(result.message)

    # Check if user said "bye" to break the loop
    if result.message.lower() == "bye":
        furhat.say(text="Goodbye!")
        break
    
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
    
    furhat.say(result.message)

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