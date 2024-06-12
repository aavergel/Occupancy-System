import flask
from flask import jsonify
from flask import request

from sql import create_connection
from sql import execute_query
from sql import execute_read_query

from random import randrange


class Creds:
    host = 'hpst'
    user = 'user'
    password = 'password'
    database = 'database'


app = flask.Flask(__name__)
app.config["DEBUG"] = True

conn = create_connection(Creds.host, Creds.user, Creds.password, Creds.database)


# RESIDENT TABLE OPERATIONS

# return all residents
@app.route('/api/resident/all', methods=['GET'])
def all_residents():
    sql = "SELECT * FROM resident"
    residents = execute_read_query(conn, sql)
    return jsonify(residents)


# return resident by id
@app.route('/api/resident', methods=['GET'])
def resident_by_id():
    request_data = request.get_json()
    someresident = request_data['residentid']

    sql = "SELECT * FROM resident WHERE residentid = '%s'" % someresident
    resident = execute_read_query(conn, sql)

    return jsonify(resident)


# add new resident
@app.route('/api/resident', methods=['POST'])
def new_resident():
    request_data = request.get_json()
    nid = randrange(100, 1000)
    fname = request_data['firstname']
    lname = request_data['lastname']
    age = request_data['age']
    roomid = request_data['roomid']
    sql = 'SELECT * FROM room'
    rooms = execute_read_query(conn, sql)
    roomids = []  # list of available rooms
    for room in rooms:
        if room['capacity'] != 0:  # check if room is not at full capacity
            roomids.append(room['roomid'])
    if roomid in roomids:  # check if room id is a valid room
        sql = "INSERT INTO resident VALUES ('%s', '%s', '%s', '%s', '%s')" % (nid, fname, lname, age, roomid)
        execute_query(conn, sql)
        sqll = 'UPDATE room SET capacity = capacity - 1'  # resident takes up 1 capacity
        execute_query(conn, sqll)

        return 'Resident added'
    else:
        return 'Error: No room'


# update resident
@app.route('/api/resident', methods=['PUT'])
def update_resident():
    request_data = request.get_json()
    someresident = request_data['residentid']
    fname = request_data['firstname']
    lname = request_data['lastname']
    age = request_data['age']
    roomid = request_data['roomid']

    sql = "UPDATE resident SET firstname = %s, lastname = %s, age = %s, roomid = %s WHERE residentid = '%s' limit 1" \
          % (fname, lname, age, roomid, someresident)
    sqll = 'SELECT * FROM room'
    rooms = execute_read_query(conn, sqll)
    for room in rooms:  # check if updating room exists
        if room['roomid'] == roomid:
            execute_read_query(conn, sql)

            return 'Resident updated'
    return 'No room selected'


# delete resident
@app.route('/api/resident', methods=['DELETE'])
def del_resident():
    request_data = request.get_json()
    idtodelete = request_data['residentid']

    sql = "DELETE FROM resident WHERE residentid = %s" % idtodelete
    execute_query(conn, sql)

    # room capacity increases if resident is removed
    sqll = 'UPDATE room SET capacity = capacity + 1 WHERE (SELECT * FROM resident WHERE residentid = %s' % idtodelete
    execute_query(conn, sqll)
    return 'Resident deleted'


app.run()

