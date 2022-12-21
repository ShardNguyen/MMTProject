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

#Get path to the file
path = address.replace(domain, "")

if path == "" or path == "/":
	path = fileToGet


#----- CONNECT -----
s.connect((domain, port)) # Connect
#<socket variable>.connect(("address", port))

get = "GET /" + path + " HTTP/1.1\r\n"
host = "Host: " + domain + "\r\n\r\n"
request = get + host
s.send(request.encode()) #send request
#Request must be encoded, so we have to use encode() function


#----- GET CONTENT LENGTH -----
# Check where content length is
contentLength = 0
#additionalLength = len(addressInfo)

for x in addressInfo._headers:
	if x[0] == "Content-Length":
		contentLength = int(x[1], base=10)
# This is to get the content length


#----- DATA WRITING -----
#open(<Name of the file>, "w") is used to open the file for writing
fileWrite = open(domain + "_" + fileToGet, "wb")
count = 0

while (count <= contentLength):
	data = s.recv(contentLength) # Get response
	#<socket variable>.recv(number of bytes of data)
	#data is used to store information that is requested above
	fileWrite.write(data)
	count += data.__sizeof__()
	#write(<Content>) is used to write the data into the file

fileWrite.close()
#nam edited
s.close()
