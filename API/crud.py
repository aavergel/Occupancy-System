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


# FLOOR TABLE OPERATIONS

# return all floors
@app.route('/api/floor/all', methods=['GET'])
def all_floors():
    sql = "SELECT * FROM floor"
    floors = execute_read_query(conn, sql)
    return jsonify(floors)


# return floor based on id //add error when no id
@app.route('/api/floor', methods=['GET'])
def floor_by_id():
    request_data = request.get_json()
    somefloor = request_data['floorid']

    sql = "SELECT * FROM floor WHERE floorid = '%s'" % somefloor
    floor = execute_read_query(conn, sql)

    return jsonify(floor)


# add new floor with auto create id (range of 3 digits)
@app.route('/api/floor', methods=['POST'])
def new_floor():
    request_data = request.get_json()
    nid = randrange(100, 1000)
    nlevel = request_data['floorlevel']
    nname = request_data['floorname']
    sql = 'SELECT * FROM floor'
    floors = execute_read_query(conn, sql)
    for floor in floors:  # check if id not previously used
        if floor['floorid'] == nid:
            nid = randrange(100, 1000)

    sql = "INSERT INTO floor VALUES ('%s', '%s', '%s')" % (nid, nlevel, nname)
    execute_query(conn, sql)

    return 'New floor added'


# update name of floor provided id
@app.route('/api/floor', methods=['PUT'])
def update_floor():
    request_data = request.get_json()
    somefloor = request_data['floorid']
    nname = request_data['floorname']
    sql = 'SELECT * FROM floor'
    floors = execute_read_query(conn, sql)
    for floor in floors:
        if floor['floorid'] == somefloor:
            sql = "UPDATE floor SET floorname = '%s' WHERE floorid = '%s' limit 1" % (nname, somefloor)
            execute_read_query(conn, sql)
            return 'Floor name updated'
        else:
            return 'No floor selected'


# delete floor by id
@app.route('/api/floor', methods=['DELETE'])
def del_floor():
    request_data = request.get_json()
    idtodelete = request_data['floorid']

    sql = "DELETE FROM floor WHERE floorid = %s" % idtodelete
    execute_query(conn, sql)
    return 'Floor deleted'

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