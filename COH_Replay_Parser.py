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
        self.mapDescription = None
        self.mapFileName = None
        self.mapWidth = None
        self.mapHeight = None
        self.playerList = []

        if filePath:
            self.load(self.filePath)

    def read_UnsignedLong4Bytes(self, fileHandle= None) -> int:
        """Reads 4 bytes as an unsigned long int."""
        try:
            fourBytes = bytearray(fileHandle.read(4))
            theInt = int.from_bytes(fourBytes, byteorder='little', signed=False)
            return theInt
        except Exception as e:
            logging.error("Failed to read 4 bytes")
            logging.exception("Stack Trace: ")

    def read_LengthString(self, fileHandle = None):
        """Reads the first 4 bytes containing the string length and then the rest of the string."""
        try:
            stringLength = self.read_UnsignedLong4Bytes(fileHandle)
            theString = self.read2byteString(fileHandle = fileHandle, stringLength =stringLength)
            return theString
        except Exception as e:
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")

    def read_2ByteString(self, fileHandle = None, stringLength=0 ) -> str:
        """Reads a 2byte encoded little-endian string of specified length."""
        try:
            theBytes = bytearray(fileHandle.read(stringLength*2))
            theString = theBytes.decode('utf-16le')
            return theString
        except Exception as e:
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")            

    def read_LengthASCIIString(self, fileHandle = None) -> str:
        """Reads ASCII string, the length defined by the first four bytes."""
        try:
            stringLength = self.read_UnsignedLong4Bytes(fileHandle)
            theString = self.read_ASCIIString(fileHandle= fileHandle, stringLength=stringLength)
            return theString
        except Exception as e:
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")  

    def read_ASCIIString(self, fileHandle = None, stringLength=0) -> str:
        """Reads a byte array of spcified length and attempts to convert it into a string."""
        try:
            theBytes = bytearray(fileHandle.read(stringLength))
            theString = theBytes.decode('ascii')
            return theString
        except Exception as e:
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")  

    def read_NULLTerminated_2ByteString(self, fileHandle = None) -> str:
        """Reads a Utf-16 little endian character string until the first two byte NULL value."""
        try:
            characters = ""
            for character in iter(partial(fileHandle.read, 2) , bytearray(b"\x00\x00")):
                characters += bytearray(character).decode('utf-16le')
            return characters    
        except Exception as e:
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")  

    def read_NULLTerminated_ASCIIString(self, fileHandle = None) -> str:
        """Reads a byte array until the first NULL and converts to a string."""
        try:
            characters = ""
            for character in iter(partial(fileHandle.read, 1) , bytearray(b"\x00")):
                characters += bytearray(character).decode('ascii')
            return characters  
        except Exception as e:
            logging.error("Failed to read a string of specified length")
            logging.exception("Stack Trace: ")  



    def load(self, filePath = ""):
        with open(filePath, "rb") as fileHandle:
            self.fileVersion = self.read_UnsignedLong4Bytes(fileHandle= fileHandle)
            cohrec = self.read_ASCIIString(fileHandle= fileHandle, stringLength= 8)
            print("cohrec : {}".format(cohrec))
            self.localDate = self.read_NULLTerminated_2ByteString(fileHandle=fileHandle)
            fileHandle.seek(2, 1) #move extra two bytes to keep in 4 byte frame of reference at end of string
            print("pointer : {}".format(fileHandle.tell()))
            for x in range(7):
                print(self.read_UnsignedLong4Bytes(fileHandle = fileHandle))
            #self.chunkyHeaderLength = self.read_UL4(fileHandle = fileHandle)
            relicChunky = self.read_ASCIIString(fileHandle=fileHandle, stringLength=12)
            #print("relicChunky : {}".format(relicChunky))
            unknown = self.read_UnsignedLong4Bytes(fileHandle=fileHandle)
            self.chunkyVersion = self.read_UnsignedLong4Bytes(fileHandle=fileHandle) # 3
            unknown = self.read_UnsignedLong4Bytes(fileHandle = fileHandle)
            self.chunkyHeaderLength = self.read_UnsignedLong4Bytes(fileHandle= fileHandle)
            fileHandle.seek(-24,1) # sets file pointer back to start of relic chunky
            fileHandle.seek(self.chunkyHeaderLength, 1) # seeks to begining of FOLDPOST


    def parseChunk(self):
        pass

    def __str__(self) -> str:
        output = "Data:\n"
        output += "fileVersion : {}\n".format(self.fileVersion)
        output += "chunkyHeaderLength : {}\n".format(self.chunkyHeaderLength)
        output += "replayVersion : {}\n".format(self.replayVersion)
        output += "chunkyVersion : {}\n".format(self.chunkyVersion)
        output += "fileName : {}\n".format(self.fileName)
        output += "localDate : {}\n".format(self.localDate)
        output += "unknownDate : {}\n".format(self.unknownDate)
        output += "replayName : {}\n".format(self.replayName)
        output += "otherVariables : {}\n".format(self.otherVariables)
        output += "modName : {}\n".format(self.modName)
        output += "mapName : {}\n".format(self.mapName)
        output += "mapDescription : {}\n".format(self.mapDescription)
        output += "mapFileName : {}\n".format(self.mapFileName)
        output += "mapWidth : {}\n".format(self.mapWidth)
        output += "mapHeight : {}\n".format(self.mapHeight)
        output += "playerList : {}\n".format(self.playerList)
        return output


# Program Entry Starts here
# Default error logging log file location:
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s (%(threadName)-10s) [%(levelname)s] %(message)s', filename= 'Errors.log',filemode = "w", level=logging.INFO)

myCOHReplayParser = COH_Replay_Parser("temp.rec")
print(myCOHReplayParser)
