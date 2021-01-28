import sys
import logging
from functools import partial


class COH_Replay_Parser:
	"""Parses a company of heroes 1 replay to extract as much useful information from it as possible."""

	def __init__(self, filePath = None) -> None:


		self.filePath = filePath
		self.fileName = None
		self.fileVersion = None
		self.chunkyHeaderLength = None
		self.chunkyVersion = None # 3
		
		self.replayVersion = None
		self.localDate = None
		self.unknownDate = None
		self.replayName = None
		self.otherVariables = {}
		self.modName = None
		self.mapName = None
		self.mapNameFull = None
		self.mapDescription = None
		self.mapDescriptionFull = None
		self.mapFileName = None
		self.mapWidth = None
		self.mapHeight = None
		self.playerList = []

		self.data = None
		self.dataIndex = 0

		if filePath:
			self.load(self.filePath)

	def read_UnsignedLong4Bytes(self) -> int:
		"""Reads 4 bytes as an unsigned long int."""
		try:
			if self.data:
				fourBytes = bytearray(self.data[self.dataIndex:self.dataIndex+4])
				self.dataIndex += 4
				theInt = int.from_bytes(fourBytes, byteorder='little', signed=False)
				return theInt
		except Exception as e:
			logging.error("Failed to read 4 bytes")
			logging.exception("Stack Trace: ")

	def read_Bytes(self, numberOfBytes):
		"""reads a number of bytes from the data array"""
		try:
			if self.data:
				output = bytearray(self.data[self.dataIndex:self.dataIndex+numberOfBytes])
				self.dataIndex += numberOfBytes
				return output
		except Exception as e:
			logging.error("Failed to Read bytes")
			logging.exception("Stack Trace: ")


	def read_LengthString(self):
		"""Reads the first 4 bytes containing the string length and then the rest of the string."""
		try:
			if self.data:
				stringLength = self.read_UnsignedLong4Bytes()
				theString = self.read_2ByteString(stringLength =stringLength)
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")

	def read_2ByteString(self, stringLength=0 ) -> str:
		"""Reads a 2byte encoded little-endian string of specified length."""
		try:
			if self.data:
				theBytes = bytearray(self.data[self.dataIndex:self.dataIndex+(stringLength*2)])
				self.dataIndex += stringLength*2
				theString = theBytes.decode('utf-16le')
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")            

	def read_LengthASCIIString(self) -> str:
		"""Reads ASCII string, the length defined by the first four bytes."""
		try:
			if self.data:
				stringLength = self.read_UnsignedLong4Bytes()
				theString = self.read_ASCIIString(stringLength=stringLength)
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def read_ASCIIString(self, stringLength=0) -> str:
		"""Reads a byte array of spcified length and attempts to convert it into a string."""
		try:
			if self.data:
				theBytes = bytearray(self.data[self.dataIndex:self.dataIndex+stringLength])
				self.dataIndex += stringLength
				theString = theBytes.decode('ascii')
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def read_NULLTerminated_2ByteString(self) -> str:
		"""Reads a Utf-16 little endian character string until the first two byte NULL value."""
		try:
			if self.data:
				characters = ""
				for character in iter(partial(self.read_Bytes, 2) , bytearray(b"\x00\x00")):
					characters += bytearray(character).decode('utf-16le')
				return characters    
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def read_NULLTerminated_ASCIIString(self) -> str:
		"""Reads a byte array until the first NULL and converts to a string."""
		try:
			if self.data:
				characters = ""
				for character in iter(partial(self.read_Bytes, 1) , bytearray(b"\x00")):
					characters += bytearray(character).decode('ascii')
				return characters  
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def seek(self, numberOfBytes, relative = 0):
		"""Moves the file index a number of bytes forward or backward"""
		try:
			numberOfBytes = int(numberOfBytes)
			relative = int(relative)
			if relative == 0:
				assert(0 <= numberOfBytes <= len(self.data))
				self.dataIndex = numberOfBytes
			if relative == 1:
				assert(0 <= (numberOfBytes+self.dataIndex) <= len(self.data))
				self.dataIndex += numberOfBytes
			if relative == 2:
				assert(0 <= (len(self.data) - numberOfBytes) <= len(self.data))
				self.dataIndex = len(self.data) - numberOfBytes
		except Exception as e:
			logging.error("Failed move file Index")
			logging.exception("Stack Trace: ")
			return None          



	def load(self, filePath = ""):
		with open(filePath, "rb") as fileHandle:
			self.data = fileHandle.read()
		self.processData()

	def processData(self):

		#Process the file Header
		self.fileVersion = self.read_UnsignedLong4Bytes()
		cohrec = self.read_ASCIIString(stringLength= 8)
		print("cohrec : {}".format(cohrec))

		self.localDate = self.read_NULLTerminated_2ByteString()
		#if (len(self.localDate)% 2 == 0):
		#	self.seek(2, 1) #move extra two bytes to keep in 4 byte frame of reference at end of string
		#print("dataIndex : {}".format(self.dataIndex))
		self.seek(76,0)

		firstRelicChunkyAddress = self.dataIndex
		relicChunky = self.read_ASCIIString(stringLength=12)
		print("relicChunky : {}".format(relicChunky))
		unknown = self.read_UnsignedLong4Bytes()
		self.chunkyVersion = self.read_UnsignedLong4Bytes() # 3
		unknown = self.read_UnsignedLong4Bytes()
		self.chunkyHeaderLength = self.read_UnsignedLong4Bytes()
		self.seek(-28,1) # sets file pointer back to start of relic chunky
		self.seek(self.chunkyHeaderLength, 1) # seeks to begining of FOLDPOST

		self.seek(firstRelicChunkyAddress, 0)
		self.seek(96,1) # move pointer to the position of the second relic chunky
		secondRelicChunkyAddress = self.dataIndex

		relicChunky = self.read_ASCIIString(stringLength=12)

		unknown = self.read_UnsignedLong4Bytes()
		chunkyVersion = self.read_UnsignedLong4Bytes() # 3
		unknown = self.read_UnsignedLong4Bytes()
		chunkLength = self.read_UnsignedLong4Bytes()
		
		self.seek(secondRelicChunkyAddress, 0)
		self.seek(chunkLength, 1) # seek to position of first viable chunk

		self.parseChunk(0)
		self.parseChunk(0)

		#get mapname and mapdescription from ucs file if they exist there
		self.mapNameFull = UCS().compareUCS(self.mapName)
		self.mapDescriptionFull = UCS().compareUCS(self.mapDescription)


	def parseChunk(self, level):

		print("LEVEL : {}".format(level))
		
		
		print("dataIndex {} ".format(self.dataIndex))
		chunkType = self.read_ASCIIString(stringLength= 8) # Reads FOLDFOLD, FOLDDATA, DATASDSC, DATAINFO etc
		print("chunkType : {}".format(chunkType))

		chunkVersion = self.read_UnsignedLong4Bytes()
		print("chunkVersion : {}".format(chunkVersion))
		chunkLength = self.read_UnsignedLong4Bytes()
		print("chunkLength : {}".format(chunkLength))
		chunkNameLength = self.read_UnsignedLong4Bytes()
		print("chunkNameLength : {}".format(chunkNameLength))
		#print("dataIndex {} ".format(self.dataIndex))
		self.seek(8,1)
		#print("dataIndex {} ".format(self.dataIndex))
		chunkName = ""
		if chunkNameLength > 0:
			chunkName = self.read_ASCIIString(stringLength=chunkNameLength)
			print("chunkName : {}".format(chunkName))

		
		#print("chunkVersion {}, chunkLength {}, chunkNameLength {}, chunkName {}".format(chunkVersion, chunkLength, chunkNameLength, chunkName))

		chunkStart = self.dataIndex

		#Here we start a recusive loop
		if (chunkType.startswith("FOLD")):
			print("STATS WITH FOLD")
			while (self.dataIndex < (chunkStart + chunkLength )):
				self.parseChunk(level=level+1)

		if (chunkType == "DATASDSC") and (int(chunkVersion) == 2004):

			unknown = self.read_UnsignedLong4Bytes()
			self.unknownDate = self.read_LengthString()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			self.modName = self.read_LengthASCIIString() 
			self.mapFileName = self.read_LengthASCIIString()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			self.mapName = self.read_LengthString()
			
			value = self.read_UnsignedLong4Bytes() 
			if value != 0: # test to see if data is replicated or not
				unknown = self.read_2ByteString(value)
			self.mapDescription = self.read_LengthString()
			unknown = self.read_UnsignedLong4Bytes()
			self.mapWidth = self.read_UnsignedLong4Bytes()
			self.mapHeight = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes() 

		if(chunkType == "DATABASE") and (int(chunkVersion == 11)):

			print("Got to DATABASE")

			self.seek(16, 1)

			self.randomStart = (self.read_UnsignedLong4Bytes() == 0)
			
			COLS = self.read_UnsignedLong4Bytes()
			
			self.highResources = (self.read_UnsignedLong4Bytes() == 1)

			TSSR = self.read_UnsignedLong4Bytes()
			
			self.VPCount = 250 * (1 << (int)(self.read_UnsignedLong4Bytes()))

			self.seek(5, 1)

			self.replayName = self.read_LengthString()

			self.seek(8, 1)

			self.VPGame = (self.read_UnsignedLong4Bytes() ==  0x603872a3)

			self.seek(23 , 1)
			self.read_LengthASCIIString()
			self.seek(4,1)
			self.read_LengthASCIIString()
			self.seek(8,1)
			if (self.read_UnsignedLong4Bytes() == 2):
				self.read_LengthASCIIString()
				self.gameVersion = self.read_LengthASCIIString()
			self.read_LengthASCIIString()
			self.matchType = self.read_LengthASCIIString()

		if(chunkType == "DATAINFO") and (chunkVersion == 6):

			print("got to DATAINFO")
			userName = self.read_LengthString()
			self.read_UnsignedLong4Bytes()
			self.read_UnsignedLong4Bytes()
			faction = self.read_LengthASCIIString()
			self.read_UnsignedLong4Bytes()
			self.read_UnsignedLong4Bytes()
			self.playerList.append((userName,faction))


		self.seek(chunkStart + chunkLength, 0)

	def __str__(self) -> str:
		output = "Data:\n"
		output += "fileVersion : {}\n".format(self.fileVersion)
		output += "chunkyVersion : {}\n".format(self.chunkyVersion)
		output += "randomStart : {}\n".format(self.randomStart)
		output += "highResources : {}\n".format(self.highResources)
		output += "VPCount : {}\n".format(self.VPCount)
		output += "matchType : {}\n".format(self.matchType)
		output += "localDate : {}\n".format(self.localDate)
		output += "unknownDate : {}\n".format(self.unknownDate)
		output += "replayName : {}\n".format(self.replayName)
		output += "gameVersion : {}\n".format(self.gameVersion)
		output += "modName : {}\n".format(self.modName)
		output += "mapName : {}\n".format(self.mapName)
		output += "mapNameFull : {}\n".format(self.mapNameFull)
		output += "mapDescription : {}\n".format(self.mapDescription)
		output += "mapDescriptionFull : {}\n".format(self.mapDescriptionFull)
		output += "mapFileName : {}\n".format(self.mapFileName)
		output += "mapWidth : {}\n".format(self.mapWidth)
		output += "mapHeight : {}\n".format(self.mapHeight)
		output += "playerList : {}\n".format(len(self.playerList))
		output += "playerList : {}\n".format(self.playerList)
		return output

class UCS:
	def __init__(self) -> None:
		self.cohPath = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch"
		self.ucsPath = "C:\Program Files (x86)\Steam\steamapps\common\Company of Heroes Relaunch\CoH\Engine\Locale\English\RelicCOH.English.ucs"

	def compareUCS(self, compareString):
		try:
			linenumber = 1
			with open(self.ucsPath, "r", encoding="utf-16") as f:	
				for line in f:
					linenumber += 1
					firstString = str(line.split('\t')[0])
					if str(compareString[1:].strip()) == str(firstString):
						if len(line.split('\t')) > 1:
							return " ".join(line.split()[1:])
		except Exception as e:
			logging.error(str(e))
			logging.exception("Stack : ")



# Program Entry Starts here
# Default error logging log file location:
for handler in logging.root.handlers[:]:
	logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s (%(threadName)-10s) [%(levelname)s] %(message)s', filename= 'Errors.log',filemode = "w", level=logging.INFO)

myCOHReplayParser = COH_Replay_Parser("temp5.rec")
print(myCOHReplayParser)
