from flask import Flask, render_template, request, jsonify
import pandas as pd

loadList = []

manifest_name = "SS TEST SHIP"
employee_name = "John Doe"

manifests = []
for case in range(1,6):
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
@app.route("/choice")

#homepage route
def home_page():
    return render_template('test.html',MANIFEST_NAME=manifest_name, EMPLOYEE_NAME=employee_name, manifest=manifestMatrix)
@app.route("/addContainer", methods=["POST"])
def addContainer():
    if request.method == "POST":
        text = request.form
        p = (int(text["row"]), int(text["col"]))
        
        loadList.append(p)
        print(loadList)
        # first = ""
        # for i in text:
        #     first = i
        # loadList.append((first[0], first[2:]))
    return ('', 204)

@app.route("/")
def navigate():
    return render_template('homepage.html', EMPLOYEE_NAME=employee_name)



@app.route("/printList")
def printList():
    if request.is_json:
        return jsonify({"list": loadList})
    return('', 200)

#load route
@app.route("/load")
def load_page():
    return render_template('loadP1.html',MANIFEST_NAME=manifest_name, EMPLOYEE_NAME=employee_name)

#balance route
@app.route("/balance")
def balance_page():
    return "<h1>BALANCE<h1>"



#Allows site to be hosted by running python script
if __name__ == '__main__':
    app.run(debug=True)
