from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from heuristic import *
from queue import PriorityQueue
from werkzeug.utils import secure_filename
import datetime
from enum import Enum
import os


nrows=8
ncols=12

shipCase = 1

class Back:
    unloadList = []
    loadList = []
    manifest_name = ""
    employee_name = "John Doe"
    manifests = []
    readManifest = None
    buffer = None
    dictOfMoves = {}
    cost = 0
    
backend = Back()

def getEmployee():
    return backend.employee_name

def setEmployee(name):
    backend.employee_name = name
    return

def getCost():
    return backend.cost
def setCost(c):
    backend.cost = c
    return

def createLogFile():
    file1 = open("logfile.txt", 'w')        #overwrites the entire file
    file1.close()
    file2 = open("logfile_copy.txt", 'w')   #overwrites the entire file
    file2.close()
    return

def addUserCommenttoLogFile(comment):
    time = datetime.datetime.now()
    entireMessage = str(time) + tab + logMessage.INFO.name + tab + "MANUAL COMMENT FROM " + backend.employee_name.upper() + ": \"" + comment + "\"\n"

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
    print("logged comment")
    return

def printLogFile():
    file1 = open("logfile.txt", 'r')        #opens to read the file
    print(file1.read())
    return


#logFile initialization
createLogFile()

dictOfMoves = {}
l = [((0,1), (0,6)), ((0,2), (0,1)), ((1,0),(0,1)), ((2,1),(1,2)), ((2,10),(2,11))]
for i in range(len(l)):
    dictOfMoves["start " + str(i+1)] = str(l[i][0])
    dictOfMoves["end " + str(i+1)] = str(l[i][1])

# for case in range(1,6):
#     manifests = backend.manifests
#     manifests.append( pd.read_csv('../ship_cases/ShipCase'+str(case)+'.txt',header=None,names=["col","row","weight","cont"]) )
#     manifests[case-1]['col'] = manifests[case-1]['col'].str.replace("[","", regex=True)
#     manifests[case-1]['row'] = manifests[case-1]['row'].str.replace("]","", regex=True)
#     manifests[case-1]['weight'] = manifests[case-1]['weight'].str.replace("{","", regex=True).replace("}","", regex=True)
#     manifests[case-1]['cont'] = manifests[case-1]['cont'].str.replace("UNUSED","", regex=True)

# manifest = manifests[0]
# manifestMatrix = []
# for col in range(0,8):
#     rows = []
#     for row in range(0,12):
#         rows.append(manifest.loc[(col*12)+row])
#     manifestMatrix.append(rows)




# initialState, finalState, dupes, finals = branchingBalance(backend.readManifest, ncols)
# print(finalState.movesList)



tab = '  '
logMessage = Enum('logMessage', ['FATAL', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'])



# finalState.movesList
#instantiate flask app
app = Flask(__name__)

#"/" is root page of app
@app.route("/choice")

#homepage route
def home_page():
    return render_template('test.html',MANIFEST_NAME=backend.manifest_name, EMPLOYEE_NAME=backend.employee_name, manifest=backend.readManifest)
@app.route("/addContainer", methods=["POST"])
def addContainer():
    if request.method == "POST":
        text = request.form
        p = (int(text["row"]), int(text["col"]))
        
        backend.unloadList.append(p)
        print(backend.unloadList)
        # first = ""
        # for i in text:
        #     first = i
        # unloadList.append((first[0], first[2:]))
    return ('', 204)

@app.route("/")
def navigate():
    if (backend.manifest_name != ""):
        os.remove(backend.manifest_name)
        backend.manifest_name = ""
    backend.unloadList = []
    backend.loadList = []
    backend.manifests = []
    setCost(0)
    backend.dictOfMoves.clear()
    return render_template('homepage.html', EMPLOYEE_NAME=backend.employee_name)

@app.route("/services", methods=['POST'])
def services():
    if request.method == 'POST':
        uploadedFile = request.files["file"]
        uploadedFile.save(secure_filename(uploadedFile.filename))
        # backend = Back()
        # backend.unloadList = []
        # backend.loadList = []
        # backend.manifests = []
        backend.manifest_name = uploadedFile.filename
        s = "Manifest file name: (" + backend.manifest_name + ") has been uploaded"
        addContainerCommenttoLogFile(s)
        print(s)
        testManifest = ( pd.read_csv(str(uploadedFile.filename),header=None,names=["col","row","weight","cont"]) )
        testManifest['col'] = testManifest['col'].str.replace("\[| ","", regex=True)
        testManifest['row'] = testManifest['row'].str.replace("\]| ","", regex=True)
        testManifest['weight'] = testManifest['weight'].str.replace("{|}| ","", regex=True)
        testManifest['cont'] = (testManifest['cont'].str[1:])

        backend.readManifest = np.array(testManifest.loc[:]).reshape(nrows,ncols,4)
        backend.buffer = np.zeros(4*24).reshape(4,24)
    return render_template('choices.html', EMPLOYEE_NAME=backend.employee_name)

@app.route("/logIn", methods=["POST"])
def logIn():
    if request.method == "POST":
        text = request.form
        p = text["comment"]
        s1 = getEmployee() + " signed out"
        setEmployee(text["name"])
        print(s1) #addContainerCommenttoLogFile(s1)
        addContainerCommenttoLogFile(s1)
        print(p) #addContainerCommenttoLogFile(p)
        addContainerCommenttoLogFile(p)
    return ('', 204)

@app.route("/addComment", methods=['POST'])
def addComment():
    if request.method == "POST":
        text = request.form
        p = text["comment"]
        print(p) #addContainerCommenttoLogFile(p)
        addUserCommenttoLogFile(p)
    return ('', 204)

@app.route("/normalComment", methods=['POST'])
def normalComment():
    if request.method == "POST":
        text = request.form
        p = text["comment"]
        print(p) #addContainerCommenttoLogFile(p)
        addContainerCommenttoLogFile(p)
    return ('', 204)

@app.route("/printList")
def printList():
    if request.is_json:
        return jsonify({"list": backend.unloadList})
    return('', 200)

@app.route("/newContainers", methods=['POST']) 
def newContainers():
    if request.method == 'POST':
        containerName = request.form["containerName"]
        containerWeight = request.form["containerWeight"]
        p = [containerWeight, containerName]
        backend.loadList.append(p)
        s = backend.employee_name.upper() + " entered container \'" + containerName + "\' with weight " + containerWeight + " for loading"
        addContainerCommenttoLogFile(s)
        print(backend.loadList)
    return ('', 204)

@app.route("/loadService", methods=["POST"])
def loadService():
    if request.method == "POST":
        initialState, finalState, dupes, finals = LoadingBranch(backend.readManifest, backend.unloadList, backend.loadList)
        createMoveDict(finalState.movesList)
        setCost(finalState.moves)
        s = request.form["step"]
        d = {}
        d["startPos"] = backend.dictOfMoves["start " + str(s)]
        d["endPos"] = backend.dictOfMoves["end " + str(s)]
        d["name"] = backend.dictOfMoves["name " + str(s)]
        d["totalMoves"] = str(len(backend.dictOfMoves) / 3)
        # print(d)
        print(backend.dictOfMoves)
        return jsonify({"data": d})
    return("", 200)

#load route
@app.route("/load")
def load_page():
    return render_template('loadP1.html',MANIFEST_NAME=backend.manifest_name, EMPLOYEE_NAME=backend.employee_name, manifest=backend.readManifest)

#balance route
@app.route("/balance")
def balance():
    initialState, finalState, dupes, finals = branchingBalance(backend.readManifest, ncols)
    createMoveDict(finalState.movesList)
    setCost(finalState.moves)
    # ret = backend.dictOfMoves
    print(finalState.movesList)
    return render_template("balanceHtml.html", MANIFEST_NAME=backend.manifest_name, EMPLOYEE_NAME=backend.employee_name, manifest=backend.readManifest)

@app.route("/getStep", methods=['POST']) 
def getStep():
    if request.method == 'POST':
        s = request.form["step"]
        # print(request.form)
        d = {}
        d["startPos"] = backend.dictOfMoves["start " + str(s)]
        d["endPos"] = backend.dictOfMoves["end " + str(s)]
        d["name"] = backend.dictOfMoves["name " + str(s)]
        d["totalMoves"] = str(backend.cost)
        print(d)
        return jsonify({"data": d})
    return("", 200)

@app.route('/download')
def downloadManifest ():
    path = backend.manifest_name
    dot = backend.manifest_name.find('.')
    newName = backend.manifest_name[:dot] + "_UPDATED.txt"
    return send_file(path, as_attachment=True, download_name=newName)
    

def createMoveDict(testArray):
    # testArray = [[[['01', '04', '00120', 'Ram']], [1, 8]], [[['01', '09', '00035', 'Owl']], [1, 6]]]
    for i in range(len(testArray)):
        backend.dictOfMoves["start " + str(i+1)] = str(int(testArray[i][0][0][0])) +'.'+ str(int(testArray[i][0][0][1]))
        backend.dictOfMoves["end " + str(i+1)] = str(testArray[i][1][0]) + '.' + str(testArray[i][1][1])
        backend.dictOfMoves["name " + str(i+1)] = testArray[i][0][0][3]
        backend.dictOfMoves["weight " + str(i+1)] = testArray[i][0][0][2]
    return

# print (dictOfMoves)
# def solveBalance():
#     if request.method == "POST":
#         currStep = request.form["step"]
#         d = {}
#         d["start"] = dictOfMoves["start " + str(currStep)]
#         d["end"] = dictOfMoves["end " + str(currStep)]
#         # print("HERE")
#         return jsonify({"data": d})
#     return("", 200)


def createManifestCopy(doc, start, end, start_line=-1, end_line=-1):
    copy = open("manifest_copy.txt", 'w')   #overwrites the entire file
    for i in range(len(doc)-1):
        print(i)
        if i == start_line:
            copy.write(start)
        elif i == end_line:
            copy.write(end)
        else:
            copy.write(doc[i])
        copy.write('\n')
    copy.close()
    return

@app.route("/changeManifest", methods=["POST"])
def moveContainerInManifest():
    if request.method == 'POST':
        step = request.form["step"]
        both = 0
        manifest = open(backend.manifest_name,'r')
        doc = manifest.read().split('\n')
        manifest.close()
        #print("doc[1] =", doc[1])
        #print("dictOfMoves =", backend.dictOfMoves)
        
        start = "start " + str(step)
        start = backend.dictOfMoves[start]     #string
        # print("start=", start)
        c = start.find('.')
        start_row = int(start[:c])
        start_col = int(start[c+1:])

        if (start == "9.1"): both = -1
        else:
            start_line = ((start_row - 1) * 12) + (start_col - 1)
            print("start line = ",start_line)
            start = doc[start_line]                       #access to start postion in manifest
            #print("start=", start)
            #print("start_row=", start_row, "  start_col=", start_col)
        # else:
        #     start = "[9,1], {weight}, " + backend.dictOfMoves["name " + str(step)]
        o = start.find('{')
        start_data = start[o:]
        start_keep = start[:o]               #save the start data

        end = "end " + str(step)
        end = backend.dictOfMoves[end]
        c = end.find('.')
        end_row = int(end[:c])
        end_col = int(end[c+1:])
        if (end == "9.1"): both = 1
        else:
            end_line = ((end_row - 1) * 12) + (end_col - 1)
            end = doc[end_line]
        #print("end_row=", end_row, "  end_col=", end_col)
        o = end.find('{')
        end_data = end[o:]  
        end_keep = end[:o] 
        # end_data = end[10:]
        weight = backend.dictOfMoves["weight " + str(step)]
        weight = str(weight)
        print(weight)
        while len(weight) != 5:
            weight = '0' + weight
        if both == 0:
            print("start=", start, "    end=", end)
            start = start_keep + end_data
            end = end_keep + start_data #backend.dictOfMoves["name " + str(step)]
            print("start=", start, "    end=", end)
            print(backend.dictOfMoves)
            
            print(start_line, end_line)
            manifest = open(backend.manifest_name,'w')
            for i in range(len(doc)-1):
                print(i)
                if i == start_line:
                    manifest.write(start)
                elif i == end_line:
                    manifest.write(end)
                else:
                    manifest.write(doc[i])
                manifest.write('\n')
                createManifestCopy(doc, start, end, start_line, end_line)
        elif both < 0:
            print("start=", start, "    end=", end)
            start = "Not Needed"
            end = end_keep + "{" + weight + "}, " + backend.dictOfMoves["name " + str(step)]
            print("start=", start, "    end=", end)
            print(backend.dictOfMoves)
            
            print(end_line)
            manifest = open(backend.manifest_name,'w')
            for i in range(len(doc)-1):
                print(i)
                if i == end_line:
                    manifest.write(end)
                else:
                    manifest.write(doc[i])
                manifest.write('\n')
                createManifestCopy(doc, start, end, end_line)
        elif both > 0:
            print("start=", start, "    end=", end)
            start = start_keep + "{00000}, UNUSED" #+ backend.dictOfMoves["name " + str(step)]
            end = "Not Needed"
            print("start=", start, "    end=", end)
            print(backend.dictOfMoves)
            
            print(start_line)
            manifest = open(backend.manifest_name,'w')
            for i in range(len(doc)-1):
                print(i)
                if i == start_line:
                    manifest.write(start)
                else:
                    manifest.write(doc[i])
                manifest.write('\n')
                createManifestCopy(doc, start, end, start_line)
        manifest.close()
    return ('', 204)


#Allows site to be hosted by running python script
if __name__ == '__main__':
    app.run(debug=True)
