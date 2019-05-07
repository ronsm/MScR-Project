from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/json-test', methods=['GET', 'POST'])
def jsonexample():
    if (request.data):
        data = request.data
        dataDict = json.loads(data)
        print(dataDict)
    return 'OK'

if __name__=='__main__':
    app.run(debug=True, port=5000, host='0.0.0.0') #run app in debug mode on port 5000