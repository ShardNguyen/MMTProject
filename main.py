import socket
import urllib.request
import os

#current Target: DOWNLOAD FOLDER
def downloadFile(downloadPath: str, fileName: str, savePath = ""):	#path to save || File name

	# ----- CREATING SOCKET -----
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#socket.socket(addr_family, type)
	#This is used to create a socket
	#socket.AF_INET is IPv4
	#socket.SOCK_STREAM is TCP

	domain = address.split('/',1)[0]
	downloadPath = address.replace(domain,"")


	#----- CONNECT -----
	s.connect((domain, DEFAULT_PORT)) # Connect
	#<socket variable>.connect(("address", port))

	get = "GET /" + downloadPath + " HTTP/1.1\r\n"
	host = "Host: " + domain + "\r\n\r\n"
	request = get + host
	s.send(request.encode()) #send request
	#Request must be encoded, so we have to use encode() function


	#----- GET CONTENT LENGTH -----
	contentLength = 1024



	#----- GET HEADER ------
	header = s.recv(contentLength)
	headerStop = header.find(b'\r\n\r\n')
	while (headerStop == -1):
		header += s.recv(contentLength)


	with open(savePath + ('/' if savePath else '') + fileName, "wb") as fileWrite:

			#Write redundant bytes in last header recv to the file, which are not header but Content
		notHeader = header.rsplit(b'\r\n\r\n')[0]
		fileWrite.write(notHeader)
		count = notHeader.__sizeof__()

		#Get Content-Length from header
		contentLengthIndex = header.find(b'Content-Length:')
		contentLength = int(header[contentLengthIndex + 16: header.find(b'\r\n', contentLengthIndex + 16)].decode())
				
		while (count <= contentLength):
			data = s.recv(contentLength) # Get response
			#<socket variable>.recv(number of bytes of data)
			#data is used to store information that is requested above
			fileWrite.write(data)
			count += data.__sizeof__() 	#increase the count by number of read bytes

	#----- Close Socket -----
	s.close()




def downloadFolder():
	partsList = address.split('/')
	domain = partsList[0]


	#----- Create folder: domain_folderName ------
	downloadFolderName = domain + '_' + partsList[-1]
	if not os.path.exists(downloadFolderName):
		os.mkdir(downloadFolderName)


	#----- DOWNLOAD index.html -----
	downloadFile(address, 'index.html', downloadFolderName)

	#----- Parsing the index.html -----
	fin = open('index.html', 'r')	




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


	#if the last part contain '.' -> means it's a file, then downloadFile
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