from flask import Flask, jsonify
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
measurements = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route('/')
def home():
    output = (
        '<h1>Welcome to Hawaii Climate App</h1>'
        '<p>Please select a link to get weather info:</P>'
        '<ul>'
            '<li><a href="/api/v1.0/precipitation">Precipitation</a></li>'
            '<li><a href="/api/v1.0/stations">Stations</a></li>'
            '<li><a href="/api/v1.0/tobs">Temperatures</a></li>'
            '<li>/api/v1.0/"start date"</li>'
            '<li>/api/v1.0/"start date"/"end date"</li>'
            # '<li>Start date <input name="start" placeholder="2016-8-23">'
            # '<li>End date <input name="end" placeholder="2016-9-10">'

        '</ul>'
    )

    return output

@app.route('/api/v1.0/precipitation')
def prcp():
    strDate = session.query(func.max(measurements.date)).first()[0]
    lastDate = dt.datetime.strptime(strDate, '%Y-%m-%d')
    prevYear = lastDate - dt.timedelta(365)

    result = session.query(measurements.date, measurements.prcp)\
            .filter(measurements.date>=prevYear).all()

    return { date:prcp for date, prcp in result }

@app.route('/api/v1.0/stations')
def stations_call():
    stations_list = session.query(stations.station,stations.name).all()

    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def temps():
    strDate = session.query(func.max(measurements.date)).first()[0]
    lastDate = dt.datetime.strptime(strDate, '%Y-%m-%d')
    prevYear = lastDate - dt.timedelta(365)

    most_active_station = session.query(measurements.station,func.count()).group_by(measurements.station).order_by(func.count().desc()).first()[0]

    temps_list = session.query(measurements.date,measurements.tobs).filter((measurements.station == most_active_station) & (measurements.date >= prevYear)).all()

    return { date:tobs for date,tobs in temps_list }

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def startEnd(start,end='2017-08-23'):

    result = session.query(func.min(measurements.tobs),func.max(measurements.tobs),func.avg(measurements.tobs).filter((measurements.date>=start) & (measurements.date <= end))).all()[0]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)