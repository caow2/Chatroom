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
	if address in clients:
		return
	clients.add(address)
	welcomeMsg = 'Welcome to the chatroom! There are currently %s total users.' % str(len(clients))
	broadcastMsg = 'User %s has joined the chatroom.' % str(address)
	sendMessage(address, welcomeMsg)
	broadcastMessage(address, broadcastMsg, server=True)


# Removes a client address from set of clients and notifies the chatroom.
# Assumes client exists in set.
def quit(address):
	removeClient(address)
	quitMsg = 'You have left the chatroom. Thanks!'
	broadcastMsg = 'User %s has left the chatroom.' % str(address)
	sendMessage(address, quitMsg)
	broadcastMessage(address, broadcastMsg, server=True)


def removeClient(address):
	clients.remove(address)
	if address in muted:
		muted.remove(address)


# Broacasts a received message to all unmuted clients except the sender address.
# If server is True, then the server is original sender of message. 
# (Used for making server announcemnts like user joining/quitting etc.)
#
# Clients should receive message in the form:
# ClientID:
#		message\n
def broadcastMessage(address, message, server=False):
	message = processRcvMessage(message)
	# Only print if receiving message from client
	if not server:
		print('RECEIVED message from %s:\n\t%s\n' % (str(address), message))
	sender = 'SERVER' if server else str(address)
	for client in clients:
		if(client != address and client not in muted):
			sendMessage(client, message, sender)


# Sends a message to the specified address.
# default sender is the server if not specified
def sendMessage(receiver, message, sender='SERVER'):
	message = processSendMessage(sender, message)
	serverSocket.sendto(message.encode(), receiver);
	print('SENT message to %s:\n\t%s' %  (str(receiver), message))


# Mutes the client. Assumes they exist in set of clients.
def mute(address):
	if address in muted:
		userMsg = 'You are already muted.'
	else:
		muted.add(address)
		userMsg = 'You have been muted from the chatroom.'
		broadcastMsg = 'User %s has opted to be muted.' % str(address)
		broadcastMessage(address, broadcastMsg, server=True)
	sendMessage(address, userMsg)

# Unmutes the client. Assumes they exist in set of clients.
def unmute(address):
	if address not in muted:
		return  # Already unmuted
	muted.remove(address)
	unmuteMsg = 'You have been unmuted from the chatroom.'
	broadcastMsg = 'User %s has been opted to be unmuted.' % str(address)
	sendMessage(address, unmuteMsg)
	broadcastMessage(address, broadcastMsg, server=True)


# Sends list of active clients to specified address
def getUsers(address):
	message = 'ACTIVE CLIENTS:\n'
	for client in clients:
		message += '\t' + str(client) + '\n'
	message = message.strip() #remove last \n
	sendMessage(address, message)


# Preprocess message before it is sent
def processSendMessage(sender, message):
	msg = '%s:\n\t%s\n' % (str(sender), message)
	return msg


# Preprocess a message that is received
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

serverPort = 8080
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('Chatroom server is ready.')

# Wait for messages
bufferSize = 2048
while True:
	message, clientAddress = serverSocket.recvfrom(bufferSize)
	message = message.decode()

	# Only consider messages from active clients
	if clientAddress in clients:
		broadcastMessage(clientAddress, message)
		if message in commands:
			commands[message](clientAddress) # run command
	elif message == JOIN_MSG:
		commands[message](clientAddress)	# or if client is attempting to join

	
