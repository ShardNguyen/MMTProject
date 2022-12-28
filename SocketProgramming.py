#----- SOCKET -----
import socket

#----- Parsing ------ 
from urllib.parse import urlparse
from urllib.parse import unquote

#----- mkdir -----
import os


def downloadFileCLength(downloadPath: str, fileName: str, savePath = ""):	#savePath has default empty value (for current directory download)

	# ----- CREATING SOCKET -----
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#socket.socket(addr_family, type)
	#This is used to create a socket
	#socket.AF_INET is IPv4
	#socket.SOCK_STREAM is TCP

	HOST = url.hostname

	#----- CONNECT -----
	s.connect((HOST, DEFAULT_PORT)) # Connect
	#<socket variable>.connect(("address", port))

	get = "GET " + downloadPath + " HTTP/1.1\r\n"
	keepAlive = 'Connection: keep-alive\r\n'
	host = "Host: " + HOST + '\r\n'
	request = get + host + keepAlive + "\r\n"

	#----- SEND REQUEST -----
	sent = s.send(request.encode()) #Request must be encoded, so we have to use encode() function
	if sent == 0:
		raise RuntimeError("socket connection broken")
	
	#----- default CONTENT-LENGTH -----
	contentLength = 4096


	#----- GET HEADER ------
	header = s.recv(contentLength)
	while (header.find(b'\r\n\r\n') == -1):
		temp = s.recv(contentLength)

		#Raise error if recv NOTHING
		if temp.__sizeof__ == 0:
			raise RuntimeError("socket connection broken")
		header += temp


	#----- 404 HANDLING ------
	if header.find(b'404 Not Found') != -1:
		print('Error 404 Not Found ', fileName )
		return
	if header.find(b'301 Moved Permanently') != -1:
		print('Error 301 Moved Permanently')
		return


	#----- WRITE TO FILE ------
	fileName = unquote(fileName) #to decode URL special characters (i.e. %20 means whitespace: ' ')
	print('Downloading ',fileName)
	with open(savePath + ('/' if savePath else '') + (fileName if fileName else 'index.html'), "wb") as fileWrite:

			#Write redundant bytes in last header recv to the file, which are not header but Content
		notHeader = header.split(b'\r\n\r\n', 1)[1]
		fileWrite.write(notHeader)
		count = notHeader.__sizeof__()

		#Get Content-Length from header
		contentLengthIndex = header.find(b'Content-Length:')
		n = header[contentLengthIndex + 16: header.find(b'\r\n', contentLengthIndex + 16)].decode()
		contentLength = int(n)
		
		while (count <= contentLength):
			data = s.recv(contentLength) # Get response
			
			#Raise error if recv NOTHING
			if data.__sizeof__ == 0:
				raise RuntimeError("socket connection broken")
			#<socket variable>.recv(number of bytes of data)
			#data is used to store information that is requested above
			fileWrite.write(data)
			count += data.__sizeof__() 	#increase the count by number of read bytes

	#----- Close Socket -----
	s.close()




def downloadFolder():
	partsList = url.path.rstrip('/').split('/')
	domain = url.hostname

	#----- Create folder: domain_folderName ------
	downloadFolderName = domain + '_' + partsList[-1]
	if not os.path.exists(downloadFolderName):
		os.mkdir(downloadFolderName)


	#----- DOWNLOAD index.html -----
	downloadFile(url.path, '', downloadFolderName)

	#----- Parsing the index.html and looping downloadFile-----
	with open(downloadFolderName + '/index.html', 'r') as fin:
		indexHTML = fin.read()

	URLindex = 0
	while (1):
		URLindex = indexHTML.find('href="', URLindex)
		if (URLindex == -1):
			print('Complete Download the folder ', downloadFolderName)
			break
		#Move the index to file start pos (6 is size of 'href="')
		URLindex += 6

		#Extract fileName from index.html
		fileName = indexHTML[URLindex : indexHTML.find('"', URLindex)]

		#if the fileName is not a file name:
		if (fileName.find('.') == -1):
			continue

		#----- DOWNLOAD a FILE from FOLDER -----
		downloadFile(url.path + fileName, fileName, downloadFolderName)




if __name__ == "__main__":
	#----- GETTING THINGS READY -----
	address = input("Enter address: ")
	url = urlparse(address)

	DEFAULT_PORT = 80

	#if the path contain '.' -> means it's a file, then downloadFile
	if (url.path.find('.') == -1):
		downloadFolder()
	else:
		downloadFile(url.path, url.hostname + '_' + url.path.rstrip('/').split('/')[-1])