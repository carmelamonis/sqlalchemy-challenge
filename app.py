import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#Create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#Save table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flash setup
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii API! <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/><br/>"

        f"Place date (YYYY-MM-DD) to get data from a start range (may also include end range) <br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate"
    )

#Convert query results to a dictionary using date as key, and prcp as value
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        data.append(prcp_dict)

    return jsonify(data)

@app.route("/api/v1.0/stations")
def stations():
    
    #Create session
    session = Session(engine)
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()

    station_data = []
    for stat, name, lat, lon, el in results:
        stat_dict = {}
        stat_dict['Station ID'] = stat
        stat_dict['Name'] = name
        stat_dict['Latitude'] = lat
        stat_dict['Longitude'] = lon
        stat_dict['Elavation'] = el
        station_data.append(stat_dict)

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def temperature():
    #Create session
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.date <= '2017-08-23').\
        filter(Measurement.station == 'USC00519281').all()
    session.close()

    temp_list = [temp for temp in results]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        group_by(Measurement.date).filter(Measurement.date >= start).all()
    session.close()
    start_list = []
    for date, min, max, avg in results:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['TMIN'] = min
        temp_dict['TMAX'] = max
        temp_dict['TAVG'] = avg
        start_list.append(temp_dict)
    return jsonify(start_list)

    return

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        group_by(Measurement.date).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    start_list = []
    for date, min, max, avg in results:
        temp_dict = {}
        temp_dict['Date'] = date
        temp_dict['TMIN'] = min
        temp_dict['TMAX'] = max
        temp_dict['TAVG'] = avg
        start_list.append(temp_dict)
    return jsonify(start_list)


if __name__ == "__main__":
    app.run(debug=True)
