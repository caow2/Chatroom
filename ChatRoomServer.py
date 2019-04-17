from socket import *

'''
Server side of ChatRoom application.

The Chatroom is based on UDP in order to broadcast/multicast messages to a 
set of users. 
(Compared to TCP, which doesn't have this functionality and relies on 
maintaining connection)

Users are added to this set when they run the application. 
Ideally, the identification for a user should be their IP Address.

A set of commands is also provided to the user.

For all messages received, assume they are already preprocessed by client
and server just needs to broadcast it.
'''

#################
### FUNCTIONS ###
#################
# Adds a client to the set of clients and notifies the chatroom
def join(address):
	clients.add(address)
	welcomeMsg = 'Welcome to the chatroom! There are currently %s total users.' % str(len(clients))
	broadcastMsg = 'User %s has joined the chatroom.' % str(address)
	sendMessage(address, welcomeMsg, server=True)
	broadcastMessage(address, broadcastMsg, server=True)

# Removes a client address from set of clients and notifies the chatroom.
def quit(address):
	clients.remove(address)
	quitMsg = 'You have left the chatroom. Thanks!'
	broadcastMsg = 'User %s has left the chatroom.' % str(address)
	sendMessage(address, quitMsg, server=True)
	broadcastMessage(address, broadcastMsg, server=True)

# Broacasts a received message to all clients except the sender address.
# If server is True, then the server is original sender of message. 
# (Used for making server announcemnts like user joining/quitting etc.)
#
# Clients should receive message in the form:
# ClientID:
#		message\n
def broadcastMessage(address, message, server=False):
	message = processRcvMessage(message)
	print('RECEIVED message from %s:\n\t%s\n' % (str(address), message))
	for client in clients:
		if(client != address and client not in muted):
			sendMessage(client, message, server)

# Sends a message to the specified address.
def sendMessage(address, message, server=False):
	sender = (ServerName if server else address)
	message = processSendMessage(sender, message)
	serverSocket.sendto(message.encode(), address);
	print('SENT message to %s:\n\t%s' %  (str(address), message))

def mute(address):
	muted.add(address)
	muteMsg = 'You have been muted from the chatroom.'
	broadcastMsg = 'User %s has opted to be muted.' % str(address)
	sendMessage(address, muteMsg, server=True)
	broadcastMessage(address, broadcastMsg, server=True)

def unmute(address):
	muted.remove(address)
	unmuteMsg = 'You have been unmuted from the chatroom.'
	broadcastMsg = 'User %s has been opted to be unmuted.' % str(address)
	sendMessage(address, unmuteMsg, server=True)
	broadcastMessage(address, broadcastMsg, server=True)

def getUsers(address):
	message = 'ACTIVE CLIENTS:\n'
	for client in clients:
		message += '\t' + str(client) + '\n'
	message = message.strip() #remove last \n
	sendMessage(address, message, server=True)

# Preprocess message
def processSendMessage(sender, message):
	msg = '%s:\n\t%s\n' % (str(sender), message)
	return msg

def processRcvMessage(message):
	return message.strip()

##############################
### SETUP AND START SERVER ###
##############################
clients = set()
muted = set()

# Commands that require no arguments except the client's address
JOIN_MSG = '!join'
commands = {JOIN_MSG: join,
			'!quit': quit,
			'!mute': mute,
			'!unmute': unmute,
			'!users': getUsers }

ServerName = 'SERVER' # Used for sending server messages
serverPort = 8080
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('Chatroom server is ready.')

# Wait for messages
bufferSize = 2048
while True:
	message, clientAddress = serverSocket.recvfrom(bufferSize)
	message = message.decode()

	# Only broadcast messages from active clients
	if clientAddress in clients or message == JOIN_MSG:
		if message in commands:
			commands[message](clientAddress) # run command
		else:
			broadcastMessage(clientAddress, message)

	
