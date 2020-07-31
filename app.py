# Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available routes"""
    return(
        f"Available Routes: <br/>"

        f"For Precipitation: /api/v1.0/precipitation<br/>"
        f"Returns Jsonify dictionary of dates and Precepitation<br/><br/>"

        f"For list of Stations: /api/v1.0/stations<br/>"
        f"Returns Jasonify list of stations <br/><br/>"

        f"For last year temperatures: /api/v1.0/tobs<br/>"
        f"Returns Jsonify dictionary of Temperature Observations for last year<br/><br/>"

        f"Temperature result from the date in format (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Returns an Average, Max, and Min temperatures from given start date of dataset<br/><br/>"

        f"Temperature result from start date to end date in format (yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"Returns an Average, Max, and Min temperatures for a given date range"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and precipitations"""   
    # Query all precipitations
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    # Create a dictionary from the row data and append to a list
    precipitation_data = []
    for date, precipitation in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = precipitation
        precipitation_data.append(prcp_dict)

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)


# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature observations for previous year"""
    # Query last year of temperature observations
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= query_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    tobs_data = []
    for date, temperature in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = temperature
        tobs_data.append(temp_dict)

    return jsonify(tobs_data)


# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a Jsonify list of minimum temperature, average temperature, and max temperature from given start date"""

    # convert date to yyyy-mm-dd format
    start_date = datetime.strptime(start, "%Y-%m-%d").date()

    # query data from start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    session.close()

    # Create a dictionary
    temp_result = []
    for result in results:
        temp = {}
        temp["Min_Temp"] = result[0]
        temp["Avg_Temp"] = result[1]
        temp["Max_Temp"] = result[2]
        temp_result.append(temp)

    # jsonify the result
    return jsonify(temp_result)


#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a Jsonify list of minimum temperature, average temperature, and max temperature from the start to end date specified"""

    # Convert start and end date to yyyy-mm-dd format
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()

    # query data for the start date to end date 
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    # Create a list to hold results
    temp_result = []
    for result in results:
        temp = {}
        temp["Min_Temp"] = result[0]
        temp["Avg_Temp"] = result[1]
        temp["Max_Temp"] = result[2]
        temp_result.append(temp)

    # jsonify the result
    return jsonify(temp_result)
    
if __name__ == '__main__':
    app.run(debug=True)