#----- SOCKET -----
import ClientSocket

#----- argv -----
import sys

#----- threading -----
import threading

if __name__ == "__main__":
	#----- GETTING THINGS READY -----
	if len(sys.argv) == 1:
		address = input("Enter address: ")
		ClientSocket.handleConnection(address)
	elif len(sys.argv) == 2:
		ClientSocket.handleConnection(sys.argv[1])
	else:	#Multiple URLs
		for i in range(1, len(sys.argv)):
			x = threading.Thread(target=ClientSocket.handleConnection, args=(sys.argv[i],), daemon=False)
			x.start()

		# for i in range(1, len(sys.argv)):
		# 	x.join()
		

	
	


