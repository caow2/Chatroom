from socket import *
from threading import *
import sys
import time

'''
Client side of ChatRoom application (UDP-based).

Allows users to send messages to server and receive messages that other clients
send to the server.
'''

# ANSI terminal control sequences to adjust terminal screen
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


#################
### FUNCTIONS ###
#################
# Waits for a message from server until program is terminated or client leaves chatroom.
def receiveMessage():
	bufferSize = 2048
	global run
	while run:
		message, serverAddress = clientSocket.recvfrom(bufferSize)
		print(message.decode())


# Wait for user input and send to chat server
def waitUserInput():
	global run
	while run:
		message = input()
		print(CURSOR_UP_ONE + ERASE_LINE + selfMessage(message)) # Remove user input from terminal and display it in a specific format
		clientSocket.sendto(message.encode(), serverAddress)

		if(message == QUIT_CMD):
			terminateClient()


# Modify message to display on the client
def selfMessage(message):
	address = clientSocket.getsockname()
	msg = '>You %s:\n\t%s\n' % (address, message)
	return msg



def terminateClient():
	# Give receiveMsgThread time to get message back from server before
 	# adjusting boolean flag - Probably not good idea if server traffic load is high
	time.sleep(.25)
	global run
	run = False

##############################
### SETUP AND START CLIENT ###
##############################
JOIN_CMD = '!join'
QUIT_CMD = '!quit'

serverName = ''
serverPort = 8080
serverAddress = (serverName, serverPort)
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(('',0)) # let OS pick available port

startMessage = "Use %s to join the chatroom, %s to leave the chatroom." % (JOIN_CMD, QUIT_CMD)
print(startMessage)

# Create threads to listen for user input and server messages
# Set receiveMsgThread to a daemon so when userInputThread teminates, script is done
try:
	# ** Currently unable to catch Keyboardinterrupts because threading seems to blocks Exception handling
	run = True
	userInputThread = Thread(target=waitUserInput)
	userInputThread.start()
	receiveMsgThread = Thread(target=receiveMessage, daemon=True) 
	receiveMsgThread.start()
except Exception as e:
	print(e)
	print('Unable to start application due to threading issue.')


