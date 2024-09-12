# Import necessary libraries
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np

# Set up the database connection
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the Measurement and Station tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a Flask app
app = Flask(__name__)

# Home route: list all available routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    session.close()

    # Create a dictionary from the row data
    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station).all()
    session.close()

    # Convert results to a list
    stations_list = list(np.ravel(results))
    return jsonify(stations_list)

# Temperature Observations (TOBS) route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Query the station with the most temperature observations in the last year
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Query the last 12 months of temperature observations for that station
    results = session.query(Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= '2016-08-23').all()
    session.close()

    # Convert results to a list
    tobs_list = list(np.ravel(results))
    return jsonify(tobs_list)

# Dynamic route for start date only
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    
    # Query minimum, maximum, and average temperature starting from the given date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    # Convert results to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

# Dynamic route for start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    
    # Query minimum, maximum, and average temperature between the start and end date
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Convert results to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)