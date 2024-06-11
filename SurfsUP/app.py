# Import the dependencies.
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end(enter as YYYY-MM-DD)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #Retrieve precipitation data for the last 12 months
    prev_year= dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).order_by(Measurement.date).all()

    #convert query results to a dictionary with date as key and prcp as value
    ##xpert helped with this
    precip_dict = {date: prcp for date, prcp in precip_data}

    session.close()

    #return the JSON of the dictionary
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    station_data = session.query(Station.station, Station.name).all()

    session.close()
    station_list = []
    for station in station_data:
        
        station_dict = {
            "id": station.station,
            "name": station.name
        }
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    prev_year= dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date >= prev_year).all()

    session.close()

    tobs_data = []
    for date, temp in active_temp:
        tobs_data.append({date: temp})

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_temps(start):
    session = Session(engine)
   
    start_tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    start_temps = []
    for min_temp, max_temp, avg_temp in start_tobs:
        temps = {}
        temps['Minimum Temperature'] = min_temp
        temps['Maximum Temperature'] = max_temp
        temps['Average Temperature'] = avg_temp
        start_temps.append(temps)
    
    return jsonify(start_temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    start_end_tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close()

    start_end_temps = []
    for min_temp, max_temp, avg_temp in start_end_tobs:
        temps = {}
        temps['Minimum Temperature'] = min_temp    
        temps['Maximum Temperature'] = max_temp
        temps['Average Temperature'] = avg_temp
        start_end_temps.append(temps)
    
    return jsonify(start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)


