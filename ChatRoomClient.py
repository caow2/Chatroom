from socket import *
from threading import *
import sys
from termios import tcflush, TCIOFLUSH
'''
Client side of ChatRoom application (UDP-based).

Allows users to send messages to server and receive messages that other clients
send to the server.
'''

# ANSI terminal control sequences
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

def waitUserInput():
	global run
	while run:
		message = input()
		print(CURSOR_UP_ONE + ERASE_LINE + selfMessage(message))
		clientSocket.sendto(message.encode(), serverAddress)
		# Remove user input from terminal and display it in a specific format
		
		if(message == QUIT_CMD):
			terminateClient()


def selfMessage(message):
	address = clientSocket.getsockname()
	msg = '>You %s:\n\t%s\n' % (address, message)
	return msg

def terminateClient():
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

startMessage = "Use %s to join the chatroom, %s to leave the chatroom." % (JOIN_CMD, QUIT_CMD)
print(startMessage)

# Create threads to listen for user input and server messages
try:
	run = True
	userInputThread = Thread(target=waitUserInput)
	userInputThread.start()
	receiveMsgThread = Thread(target=receiveMessage)
	receiveMsgThread.start()
except Exception as e:
	print('Unable to start threads:')
	print('\n' + e)



