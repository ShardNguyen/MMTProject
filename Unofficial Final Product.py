import socket
import urllib.request

# ----- CREATING SOCKET -----
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket.socket(addr_family, type)
#This is used to create a socket
#socket.AF_INET is IPv4
#socket.SOCK_STREAM is TCP


#----- GETTING THINGS READY -----
address = input("Enter address: ")
port = 80
#<string varible>[start:end:step]
#Used to take substring from 'start' to 'end'

#This is used to know the info of the file of the website
addressInfo = urllib.request.urlopen(address).info()

#This is to remove http://
if address[0:7:1] == "http://":
	address = address.replace("http://", "", 1)
	#Replace 1 appearance of 'http://' with '' (Basically deleting it)

#Split the address into parts
partsList = address.split('/')

#The first element of the parts list is the domain name
domain = partsList[0]

#Get the requested file name
fileToGet = "index.html"

if len(partsList) != 1 and partsList[1] != "":
	fileToGet = partsList[len(partsList) - 1]
	#The last element of the parts list is the file name
if (fileToGet.find('.') == -1):
	fileToGet += ".html"


#Get path to the file
path = address.replace(domain, "")

if path == "" or path == "/":
	path = fileToGet


#----- CONNECT -----
s.connect((domain, port)) # Connect
#<socket variable>.connect(("address", port))

get = "GET /" + path + " HTTP/1.1\r\n"
host = "Host: " + domain + "\r\n"
connection = "Connection: keep-alive\r\n"
keepAlive = "Keep-Alive: timeout=5, max=100\r\n\r\n"
request = get + host + connection + keepAlive
s.send(request.encode()) #send request
#Request must be encoded, so we have to use encode() function


#----- FILE CREATION -----
fileName = domain + "_" + fileToGet
#open(<Name of the file>, "w") is used to open the file for writing
fileWrite = open(fileName, "wb")


#----- SKIPPING HEADER -----
data = None
flag = ""

while (flag != "\r\n\r\n"):
	data = s.recv(1)
	dataDecode = data.decode()

	if (flag == "\r\n\r"):
		if (dataDecode == "\n"):
			flag += dataDecode
		else:
			flag = ""

	elif (flag == "\r\n"):
		if (dataDecode == "\r"):
			flag += dataDecode
		else:
			flag = ""

	elif (flag == "\r"):
		if (dataDecode == "\n"):
			flag += dataDecode
		else:
			flag = ""

	else:
		if (dataDecode == "\r"):
			flag += dataDecode

#----- FUNCTIONS FOR TWO TYPES OF WEBSITE -----
def contentLength(s, fileWrite, length):
	count = 0
	while (count <= length):
		data = s.recv(length) # Get response
		#<socket variable>.recv(number of bytes of data)
		#data is used to store information that is requested above
		fileWrite.write(data)
		count += data.__sizeof__()
		#write(<Content>) is used to write the data into the file

def transferEncoding(s, fileWrite):
	flag = ""
	stop = 0

	while (stop == 0):
		bytesToWriteHex = ""

		#Take the length of chunks in hex
		while (flag != "\n"):
			data = s.recv(1)
			flag = data.decode()
			if (flag != "\r"):
				bytesToWriteHex += flag

		#Convert string to int
		if (bytesToWriteHex != ""):
			bytesToWriteInt = int(bytesToWriteHex, base=16)

		#Check stop flag
		if bytesToWriteInt == 0:
			stop = 1

		#Write data
		for x in range(bytesToWriteInt):
			data = s.recv(1)
			fileWrite.write(data)

		#To write /r/n at the end message
		data = s.recv(2)
		fileWrite.write(data)

		#Reset flag
		flag = ""


#----- CHECK TYPE OF WEBSITE-----
for x in addressInfo._headers:
	if x[0] == "Content-Length":
		length = int(x[1], base=10)
		contentLength(s, fileWrite, length)
		break
	elif x[0] == "Transfer-Encoding":
		if x[1] == "chunked":
			transferEncoding(s, fileWrite)
			break


#----- FINISHED WRITING AND CLOSE SOCKET -----
fileWrite.close()
s.close()