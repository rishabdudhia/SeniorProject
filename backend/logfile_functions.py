import math
from flask import Flask

'''
Function to create LogFile (initialize logFile here)
Function to write to LogFile

This file is the only way to access the logfile and is general enough to used anytime 

ADD: every line needs time and type (e.g. INFO, ERROR)
    two functions: one for user comment, another for us
        need access to username so I can put it in the user comment.

'''

def createLogFile():
    file1 = open("logfile.txt", 'w')        #overwrites the entire file
    file1.close()
    file2 = open("logfile_copy.txt", 'w')   #overwrites the entire file
    file2.close()
    return

def addCommenttoLogFile(comment):
    file1 = open("logfile.txt", 'a')        #appends to the file if it does not exist
    file1.write(comment)
    file1.close()

    file2 = open("logfile_copy.txt", 'a')   #appends to the file if it does not exist
    file2.write(comment)
    file2.close()
    return

def printLogFile():
    file1 = open("logfile.txt", 'r')        #opens to read the file
    print(file1.read())
    return


def main():
    createLogFile()
    addCommenttoLogFile("hello")
    printLogFile()
    return

if __name__ == "__main__":
    main()
