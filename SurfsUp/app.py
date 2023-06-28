# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
meas = Base.classes.measurement
stat = Base.classes.station

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
def root():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
# to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    end_date = session.query(meas.date).order_by(meas.date.desc()).first()
    end_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    year_range = end_date - dt.timedelta(days=365)

    prcp_data = session.query(meas.date, meas.prcp).\
        filter(meas.date >= year_range).all()
    
    prcp_dict = {date: prcp for date, prcp in prcp_data}

# Return the JSON representation of your dictionary.
    return jsonify(prcp_dict)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    stat_data = session.query(stat.station).all()
    stat_list = [point[0] for point in stat_data]
    return jsonify(stat_list)

# Query the dates and temperature observations of the most-active station for the previous year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    end_date = session.query(meas.date).order_by(meas.date.desc()).first()
    end_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    year_range = end_date - dt.timedelta(days=365)
    active = session.query(meas.station, func.count(meas.station)).group_by(meas.station).order_by(func.count(meas.station).desc()).all()
    most_active = active[0][0]
    tobs = session.query(meas.date, meas.tobs).\
        filter(meas.station == most_active).\
        filter(meas.date >= year_range).all()

# Return a JSON list of temperature observations for the previous year.
    tobs_list = [temp[1] for temp in tobs]
    return jsonify(tobs_list)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/start")
@app.route("/api/v1.0/start/end")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(meas.tobs), func.avg(meas.tobs), func.max(meas.tobs)]
    if not end:
        start = dt.datetime.strptime("08232016", "%m%d%Y")
        results = session.query(*sel).\
            filter(meas.date >= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps)
    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime("08232016", "%m%d%Y")
    end = dt.datetime.strptime("08232017", "%m%d%Y")
    results = session.query(*sel).\
        filter(meas.date >= start).\
        filter(meas.date <= end).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run(debug=True)