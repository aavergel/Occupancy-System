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


app.run()
