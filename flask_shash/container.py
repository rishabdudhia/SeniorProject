from flask import Flask, render_template, request, jsonify
import pandas as pd

class Back:
    unloadList = []
    loadList = []
    manifest_name = "SS TEST SHIP"
    employee_name = "John Doe"
    manifests = []
    
backend = Back()

def getEmployee():
    return backend.employee_name

def setEmployee(name):
    backend.employee_name = name
    return

for case in range(1,6):
    manifests = backend.manifests
    manifests.append( pd.read_csv('../ship_cases/ShipCase'+str(case)+'.txt',header=None,names=["col","row","weight","cont"]) )
    manifests[case-1]['col'] = manifests[case-1]['col'].str.replace("[","", regex=True)
    manifests[case-1]['row'] = manifests[case-1]['row'].str.replace("]","", regex=True)
    manifests[case-1]['weight'] = manifests[case-1]['weight'].str.replace("{","", regex=True).replace("}","", regex=True)
    manifests[case-1]['cont'] = manifests[case-1]['cont'].str.replace("UNUSED","", regex=True)

manifest = manifests[0]

manifestMatrix = []
for col in range(0,8):
    rows = []
    for row in range(0,12):
        rows.append(manifest.loc[(col*12)+row])
    manifestMatrix.append(rows)

#instantiate flask app
app = Flask(__name__)

#"/" is root page of app
@app.route("/")

#homepage route
def home_page():
    return render_template('test.html',MANIFEST_NAME=backend.manifest_name, EMPLOYEE_NAME=backend.employee_name, manifest=manifestMatrix)
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


@app.route("/printList")
def printList():
    if request.is_json:
        return jsonify({"list": backend.unloadList})
    return('', 200)

@app.route("/newContainers", methods=['POST']) 
def newContainers():
    if request.method == 'POST':
        containerName = request.form["containerName"]
        backend.loadList.append(containerName)
        print(backend.loadList)
    return ('', 204)

#load route
@app.route("/load")
def load_page():
    return render_template('loadP1.html',MANIFEST_NAME=backend.manifest_name, EMPLOYEE_NAME=backend.employee_name)

#balance route
@app.route("/balance")
def balance_page():
    return "<h1>BALANCE<h1>"



#Allows site to be hosted by running python script
if __name__ == '__main__':
    app.run(debug=True)
