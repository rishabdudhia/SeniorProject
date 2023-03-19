import math
import datetime
from enum import Enum

'''
Function to create logfile and logfile_copy
Function to write to logfile by user
Function to write to logfile by us each time user hits enter

This file is the only way to access either logfile.
'''

tab = '  '
logMessage = Enum('logMessage', ['FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'])

def createLogFile():
    file1 = open("logfile.txt", 'w')        #overwrites the entire file
    file1.close()
    file2 = open("logfile_copy.txt", 'w')   #overwrites the entire file
    file2.close()
    return

def addUserCommenttoLogFile(comment):
    time = datetime.datetime.now()
    entireMessage = str(time) + tab + logMessage.INFO.name + tab + "Employee wants to make a note that \"" + comment + "\"\n"

    file1 = open("logfile.txt", 'a')        #appends to the file if it does not exist
    file1.write(entireMessage)
    file1.close()

    file2 = open("logfile_copy.txt", 'a')   #appends to the file if it does not exist
    file2.write(entireMessage)
    file2.close()
    return

def addContainerCommenttoLogFile(comment):
    time = datetime.datetime.now()
    entireMessage = str(time) + tab + logMessage.INFO.name + tab + comment + '\n'

    file1 = open("logfile.txt", 'a')        #appends to the file if it does not exist
    file1.write(entireMessage)
    file1.close()

    file2 = open("logfile_copy.txt", 'a')   #appends to the file if it does not exist
    file2.write(entireMessage)
    file2.close()
    return

def printLogFile():
    file1 = open("logfile.txt", 'r')        #opens to read the file
    print(file1.read())
    return


"""
def main():
    createLogFile()
    addUserCommenttoLogFile("I noticed that “Apple Valley Machine parts” is about 10% over its stated weight, may be due to the rain on top, no further action taken.")
    addUserCommenttoLogFile("I notice that the “Walmart Toasters Moreno Valley South” container has a large fresh-looking dent on the door. However, door was not breeched, so just sent a photo to head office and I am continuing with the cycle.")
    printLogFile()
    return

if __name__ == "__main__":
    main()
"""
