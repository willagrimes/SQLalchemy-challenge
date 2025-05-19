# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    """List all available API routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return last 12 months of precipitation data as JSON"""
    latest_date = session.query(func.max(Measurement.date)).scalar()
    query_date = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    precip_dict = {date: prcp for date, prcp in results}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return list of all stations"""
    results = session.query(Station.station).all()
    stations_list = [r[0] for r in results]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the most active station from last year"""
    # Get most active station
    most_active = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()[0]

    # Calculate date 1 year ago
    latest_date = session.query(func.max(Measurement.date)).scalar()
    query_date = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query TOBS
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= query_date).all()

    temps = [{date: temp} for date, temp in results]
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_only(start):
    """Return min, avg, and max temp from start date to end of dataset"""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    temps = {
        "Start Date": start,
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 1),
        "TMAX": results[0][2]
    }
    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return min, avg, and max temp for a date range"""
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    temps = {
        "Start Date": start,
        "End Date": end,
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 1),
        "TMAX": results[0][2]
    }
    return jsonify(temps)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)