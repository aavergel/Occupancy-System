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


# ROOM TABLE OPERATIONS

# return all rooms
@app.route('/api/room/all', methods=['GET'])
def all_rooms():
    sql = "SELECT * FROM room"
    rooms = execute_read_query(conn, sql)
    return jsonify(rooms)


# return room based on id
@app.route('/api/room', methods=['GET'])
def room_by_id():
    request_data = request.get_json()
    someroom = request_data['roomid']

    sql = "SELECT * FROM room WHERE roomid = '%s'" % someroom
    room = execute_read_query(conn, sql)

    return jsonify(room)


# add new room with auto create id (range of 3 digits)
@app.route('/api/room', methods=['POST'])
def new_room():
    request_data = request.get_json()
    nid = randrange(100, 1000)
    ncapacity = request_data['capacity']
    number = request_data['roomnumber']
    floorid = request_data['floorid']

    # check if id not previously used
    sql = 'SELECT * FROM room'
    rooms = execute_read_query(conn, sql)
    for room in rooms:
        if room['roomid'] == nid:
            nid = randrange(100, 1000)

    # check if floor is selected
    sql = 'SELECT * FROM floor'
    floors = execute_read_query(conn, sql)
    for floor in floors:
        if floor['floorid'] == floorid:
            number = (floor['floorlevel'] * 100) + number  # floorlevel is first digit of room number

            sql = "INSERT INTO room VALUES ('%s', '%s', '%s', '%s')" % (nid, ncapacity, number, floorid)
            execute_query(conn, sql)

            return 'Room added'
    return 'No floor selected'


# update room by id
@app.route('/api/room', methods=['PUT'])
def update_room():
    request_data = request.get_json()
    someroom = request_data['roomid']
    ncapacity = request_data['capacity']
    nroomnumber = request_data['roomnumber']
    floorid = request_data['floorid']
    sql = 'SELECT * FROM floor'
    floors = execute_read_query(conn, sql)
    for floor in floors:  # check if new floor exists
        if floor['floorid'] == floorid:
            nroomnumber = (floor['floorlevel'] * 100) + nroomnumber  # floorlevel is first digit of room number
            sql = "UPDATE room SET capacity = %s, roomnumber = %s, floorid = %s WHERE roomid = %s limit 1" % \
                  (ncapacity, nroomnumber, floorid, someroom)
            execute_read_query(conn, sql)
            return 'Room updated'

    return 'No room selected'


# delete room provided id
@app.route('/api/room', methods=['DELETE'])
def del_room():
    request_data = request.get_json()
    idtodelete = request_data['roomid']
    sql = 'SELECT * FROM room WHERE roomid = %s' % idtodelete
    checkroom = execute_read_query(conn, sql)
    for room in checkroom:
        if room['capacity'] == 0:  # if room capacity is full, not allowed to delete
            return 'No! THere are people in here!'

    sql = "DELETE FROM room WHERE roomid = %s" % idtodelete
    execute_query(conn, sql)

    return 'Room deleted'


app.run()

