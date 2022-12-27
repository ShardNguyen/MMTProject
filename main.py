import socket
import urllib.request
import os

def downloadFile(address: str, fileName: str):

	# ----- CREATING SOCKET -----
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#socket.socket(addr_family, type)
	#This is used to create a socket
	#socket.AF_INET is IPv4
	#socket.SOCK_STREAM is TCP

	domain = address.split('/',1)[0]
	path = address.replace(domain,"")
	#----- CONNECT -----
	s.connect((domain, DEFAULT_PORT)) # Connect
	#<socket variable>.connect(("address", port))

	get = "GET /" + path + " HTTP/1.1\r\n"
	host = "Host: " + domain + "\r\n\r\n"
	request = get + host
	s.send(request.encode()) #send request
	#Request must be encoded, so we have to use encode() function


	#----- DATA WRITING -----
	#open(<Name of the file>, "w") is used to open the file for writing
	fileWrite = open(domain + "_" + fileName, "wb")
	count = 0

	addressInfo = urllib.request.urlopen('https://' + address).info()
		#----- GET CONTENT LENGTH -----
	# Check where content length is
	contentLength = 0
	for x in addressInfo._headers:
		if x[0] == "Content-Length":
			contentLength = int(x[1], base=10)
			break
	
	#Receiving and Ignore the HTTP Header before get the HTTP Body
	data = s.recv(contentLength)
	headerStop = data.find(b'\r\n\r\n')
	temp = data.split(b'\r\n\r\n', 1)
	count += temp[1].__sizeof__()
	fileWrite.write(temp[1])

	while (count <= contentLength):
		data = s.recv(contentLength) # Get response
		#<socket variable>.recv(number of bytes of data)
		#data is used to store information that is requested above
		fileWrite.write(data)
		count += data.__sizeof__()
		#write(<Content>) is used to write the data into the file

	fileWrite.close()
	s.close()

def downloadFolder(url: str):
	partsList = url.split('/')
	domain = partsList[0]

	#Create folder: domain_folderName
	downloadFolderName = domain + '_' + partsList[len(partsList) - 1]
	os.mkdir(downloadFolderName)

	#download index.html
	downloadFile(url, 'index.html')


if __name__ == "__main__":


	#----- GETTING THINGS READY -----
	address = input("Enter address: ")
	DEFAULT_PORT = 80
	
	if address[0:8:1] == "https://":
		address = address.replace("http://", "", 1)
		#Replace 1 appearance of 'http://' with '' (Basically deleting it)

	#This is to remove http://
	if address[0:7:1] == "http://":
		address = address.replace("http://", "", 1)
		#Replace 1 appearance of 'http://' with '' (Basically deleting it)

	partsList = address.split('/')

	if (partsList[len(partsList) - 1].find('.') == -1):
		downloadFolder(address)
	else:
		downloadFile(address, partsList[len(partsList) - 1])


def temp():
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
	path = address.replace(domain, "")		#http://gaia.cs.umass.edu/wireshark-labs/alice.txt
											#            domain		 ||        path

	if path == "" or path == "/": #if path is empty then use default file
		path += fileToGet