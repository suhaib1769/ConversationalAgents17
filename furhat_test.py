from furhat_remote_api import FurhatRemoteAPI

# Create an instance of the FurhatRemoteAPI class, providing the address of the robot or the SDK running the virtual robot
furhat = FurhatRemoteAPI("localhost")

# Get the voices on the robot
voices = furhat.get_voices()

# Set the voice of the robot
furhat.set_voice(name='Matthew')

# Say "Hi there!"
furhat.say(text="Hey there!")


# # Listen to user speech and return ASR result
# user_input = furhat.listen().message

# result = furhat.listen_stop()

# # Perform a named gesture
# furhat.gesture(name="BrowRaise")

# print(user_input)
# print(result.message)


# Listen to user speech and return ASR result
result = furhat.listen()
print(result.message)


# Perform a named gesture
furhat.gesture(name="BrowRaise")

# Perform a custom gesture
furhat.gesture(blocking=True, body={
    "frames": [
        {
            "time": [
                20
            ],
            "params": {
                "reset": True
            }
        }
    ],
    "class": "furhatos.gestures.Gesture"
    })

# # Get the users detected by the robot 
# users = furhat.get_users()

# # Attend the user closest to the robot
# furhat.attend(user="CLOSEST")

# # Attend a user with a specific id
# furhat.attend(userid="virtual-user-1")

# # Attend a specific location (x,y,z)
# furhat.attend(location="0.0,0.2,1.0")

# # Set the LED lights
# furhat.set_led(red=200, green=50, blue=50)

# no gesture
# 04.76

# nothing
# 01.64

# only gesture
# 01.58