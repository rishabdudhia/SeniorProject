from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from heuristic import *
from queue import PriorityQueue
from werkzeug.utils import secure_filename


nrows=8
ncols=12

shipCase = 1

class Back:
    unloadList = []
    loadList = []
    manifest_name = "SS TEST SHIP"
    employee_name = "John Doe"
    manifests = []
    readManifest = None
    buffer = None
    dictOfMoves = {}
    
backend = Back()

def getEmployee():
    return backend.employee_name

def setEmployee(name):
    backend.employee_name = name
    return

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
    return render_template('homepage.html', EMPLOYEE_NAME=backend.employee_name)

@app.route("/services", methods=['POST'])
def services():
    if request.method == 'POST':
        uploadedFile = request.files["file"]
        uploadedFile.save(secure_filename(uploadedFile.filename))
        # backend = Back()
        backend.unloadList = []
        backend.loadList = []
        backend.manifests = []
        backend.manifest_name = uploadedFile.filename
        print("Manifest file name (" + uploadedFile.filename + ") has been uploaded")
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
        print(p) #addContainerCommenttoLogFile(p)
    return ('', 204)

@app.route("/addComment", methods=['POST'])
def addComment():
    if request.method == "POST":
        text = request.form
        p = text["comment"]
        print(p) #addContainerCommenttoLogFile(p)
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
        print(backend.loadList)
    return ('', 204)

#load route
@app.route("/load")
def load_page():
    return render_template('loadP1.html',MANIFEST_NAME=backend.manifest_name, EMPLOYEE_NAME=backend.employee_name, manifest=manifestMatrix)

#balance route
@app.route("/balance")
def balance():
    initialState, finalState, dupes, finals = branchingBalance(backend.readManifest, ncols)
    createMoveDict(finalState.movesList)
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
        print(d)
        return jsonify({"data": d})
    return("", 200)
    

def createMoveDict(testArray):
    # testArray = [[[['01', '04', '00120', 'Ram']], [1, 8]], [[['01', '09', '00035', 'Owl']], [1, 6]]]
    for i in range(len(testArray)):
        backend.dictOfMoves["start " + str(i+1)] = str(int(testArray[i][0][0][0])) +'.'+ str(int(testArray[i][0][0][1]))
        backend.dictOfMoves["end " + str(i+1)] = str(testArray[i][1][0]) + '.' + str(testArray[i][1][1])
        backend.dictOfMoves["name " + str(i+1)] = testArray[i][0][0][3]
    return

print (dictOfMoves)
# def solveBalance():
#     if request.method == "POST":
#         currStep = request.form["step"]
#         d = {}
#         d["start"] = dictOfMoves["start " + str(currStep)]
#         d["end"] = dictOfMoves["end " + str(currStep)]
#         # print("HERE")
#         return jsonify({"data": d})
#     return("", 200)




#Allows site to be hosted by running python script
if __name__ == '__main__':
    app.run(debug=True)



