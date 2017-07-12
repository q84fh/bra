from flask import Flask,jsonify
from peewee import *
from playhouse.shortcuts import model_to_dict
from werkzeug.routing import BaseConverter
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

database = MySQLDatabase(
    config['database']['dbname'],
    **{'user': config['database']['user'],
        'password': config['database']['password']
    }
)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Bike(BaseModel):
    bikeid = IntegerField(db_column='BikeID', null=True)
    bikeidentifier = IntegerField(db_column='BikeIdentifier', null=True)
    bikepassword = IntegerField(db_column='BikePassword', null=True)
    biketypename = CharField(db_column='BikeTypeName', null=True)
    isebike = IntegerField(db_column='IsEBike', null=True)
    spikeid = CharField(db_column='SpikeID', primary_key=True)
    time = DateTimeField()

    class Meta:
        db_table = 'bikes'

class BikeState(BaseModel):
    availabilitycode = CharField(db_column='AvailabilityCode', null=True)
    availabilitymessage = CharField(db_column='AvailabilityMessage', null=True)
    battery = IntegerField(db_column='Battery', null=True)
    latitude = FloatField(db_column='Latitude', null=True)
    locknumber = IntegerField(db_column='LockNumber', null=True)
    longitude = FloatField(db_column='Longitude', null=True)
    spikeid = CharField(db_column='SpikeID', null=True)
    stationnumber = IntegerField(db_column='StationNumber', null=True)
    id_bikes_state = PrimaryKeyField()
    time = DateTimeField()

    class Meta:
        db_table = 'bikes_state'

class Station(BaseModel):
    latitude = FloatField(db_column='Latitude')
    longitude = FloatField(db_column='Longitude')
    name = CharField(db_column='Name')
    totallocks = IntegerField(db_column='TotalLocks', null=True)
    time = DateTimeField()

    class Meta:
        db_table = 'stations'

class StationState(BaseModel):
    lockedinexternallockcount = IntegerField(
        db_column='LockedInExternalLockCount',
        null=True
    )
    totalavailablebikes = IntegerField(
        db_column='TotalAvailableBikes',
        null=True
    )
    id = IntegerField(null=True)
    id_stations_state = PrimaryKeyField()
    time = DateTimeField()

    class Meta:
        db_table = 'stations_state'

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

database.connect()

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/bike/")
def bike_list():
    bikes = []
    for bike in Bike.select():
        bikes.append(model_to_dict(bike))
    return jsonify(bikes)

@app.route("/bike/<regex('[0-9]{5}'):bikeidentifier>/")
def bike_get_bikeidentifier(bikeidentifier=None):
    return jsonify(model_to_dict(Bike.get(Bike.bikeidentifier == bikeidentifier)))

@app.route("/bike/<regex('[0-9A-Z]{10}'):spikeid>/")
def bike_get_spikeid(spikeid=None):
    return jsonify(model_to_dict(Bike.get(Bike.spikeid == spikeid)))

@app.route("/station/")
def station_list():
    stations = []
    for station in Station.select():
        stations.append(model_to_dict(station))
    return jsonify(stations)

@app.route("/station/<regex('[0-9]{1,2}'):id>/")
def station_get_id(id=None):
    return jsonify(model_to_dict(Station.get(Station.id == id)))

@app.route("/station/<regex('[0-9]{1,2}'):id>/state/")
def station_get_id_state(id=None):
    return jsonify(model_to_dict(StationState.get(StationState.id == id)))
