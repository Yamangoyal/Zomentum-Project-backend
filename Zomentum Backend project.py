# Utility Libraries
# flask is required to create a mediocre server at host network.
# flask_cors is required to required to enable the CORS flexibility across browsers.
# pymongo is a library to enable python connection to mongoDB.
# datetime manages the date and time utility.

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymongo
import datetime

# MongoDB Atlas connection URL
connection_url = 'mongodb+srv://admin:yaman96@cluster0.fsarv.mongodb.net/<dbname>?retryWrites=true&w=majority'

#  Initializing the flask server object
app = Flask(__name__)
CORS(app)
client = pymongo.MongoClient(connection_url)

# Database Connection
Database = client.get_database('movie_theatre')
# Table Connections
tickets = Database.tickets
sitedata = Database.sitedata

# Setting the time to live property and respective index with a timeout of 8 hours.
tickets.create_index("time", expireAfterSeconds=8*3600)


# Route to initiate ticket booking using passed parameters
@app.route('/book-ticket', methods=['POST'])
def bookticket():
    # Required Parameters
    name = request.json["name"]
    phonenum = request.json["phonenum"]
    timings = request.json["timings"]

    # Check for the availability of ticket at the corresponding time.
    # If ticket counter for the requested value is less than 20, ticket will be booked, else rejected.
    if timings == 12:
        queryobject = {"timings": 12}
        counter12 = Database.tickets.count_documents(queryobject)

        if counter12 < 20:
            queryobject = {"countid": "ticketid"}
            query = sitedata.find_one(queryobject)
            counter = query["ticketid"]

            queryobject = {
                'name': name,
                '_id': counter+1,
                'phonenum': phonenum,
                'timings': 12,
                'time': datetime.datetime.utcnow()
            }
            query = tickets.insert_one(queryobject)

            queryobject = {"countid": "ticketid"}
            updateobject = {"ticketid": counter+1}
            query = sitedata.update_one(queryobject, {'$set': updateobject})

        else:
            return "tickets for 12pm are full"

    elif timings == 3:
        queryobject = {"timings": 3}
        counter3 = Database.tickets.count_documents(queryobject)
        if counter3 < 20:
            queryobject = {"countid": "ticketid"}
            query = sitedata.find_one(queryobject)
            counter = query["ticketid"]

            queryobject = {
                'name': name,
                '_id': counter+1,
                'phonenum': phonenum,
                'timings': 3,
                'time': datetime.datetime.utcnow()
            }
            query = tickets.insert_one(queryobject)

            queryobject = {"countid": "ticketid"}
            updateobject = {"ticketid": counter+1}
            query = sitedata.update_one(queryobject, {'$set': updateobject})

        else:
            return "tickets for 3pm are full"

    else:
        return "invalid time"

    return "Query inserted...!!!"


# Route to initiate view ticket method.
@app.route('/view-tickets/timings/<value>/', methods=['GET'])
def viewtickets(value):
    # Objects are fetched depending on the value of timings requested for.
    queryObject = {"timings": int(value)}
    query = tickets.find(queryObject)
    # Output object.
    output = {}
    i = 0
    for x in query:
        output[i] = x
        i += 1
    return jsonify(output)


# Route to initiate user details to display the ticket present.
@app.route('/user-details/id/<value>/', methods=['GET'])
def userdetails(value):
    # Objects are fetched depending on the value of ticket id requested for.
    queryObject = {"_id": int(value)}
    query = tickets.find(queryObject)
    # Output object.
    output = {}
    i = 0
    for x in query:
        output[i] = x
        i += 1
    return jsonify(output)


# Route to delete the user details/ ticket mentioned in the request.
@app.route('/delete/', methods=['POST'])
def delete():
    _id = request.json["_id"]
    # Object can be identified using the ID mentioned.
    queryObject = {
        '_id': _id,
    }
    tickets.delete_one(queryObject)
    return "Query deleted successfully"


# Route to update the user details/ ticket mentioned in the request.
@app.route('/update/id/<idval>/<updateValue>', methods=['GET'])
def update(idval, updateValue):
    # Object can be fetched depending on the ID value.
    queryObject = {"_id": int(idval)}
    # Data to be updated is mentioned as an update object.
    updateObject = {"timings": int(updateValue)}
    Query = ""
    updateValue = int(updateValue)

    # Ticket are updated only if seats are available for the other show.
    if updateValue == 3:
        counter3 = Database.tickets.count_documents({"timings": 3})
        if counter3 < 20:
            Query = tickets.update_one(queryObject, {'$set': updateObject})
        else:
            return "tickets for 3pm are full"

    elif updateValue == 12:
        counter12 = Database.tickets.count_documents({"timings": 12})
        if counter12 < 20:
            Query = tickets.update_one(queryObject, {'$set': updateObject})
        else:
            return "tickets for 12pm are full"

    # Request acknowledgement.
    if Query.acknowledged:
        return "Update Successful"
    else:
        return "Update Unsuccessful"


# Activates the flask server in the debug mode.
if __name__ == '__main__':
    app.run(debug=True)
