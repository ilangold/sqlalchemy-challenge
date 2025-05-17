# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurements = Base.classes.measurement

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
    return (
        f"<h1>Welcome to the Climate API</h1>"
        f"<p>Available Routes:</p>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        f"<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        f"<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        f"<li><a href='/api/v1.0/2017-01-01'>/api/v1.0/&lt;start&gt;</a> (e.g. 2017-01-01)</li>"
        f"<li><a href='/api/v1.0/2017-01-01/2017-08-23'>/api/v1.0/&lt;start&gt;/&lt;end&gt;</a> (e.g. 2017-01-01/2017-08-23)</li>"
        f"</ul>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(func.max(Measurements.date)).scalar()
    start_date = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)
    results = session.query(Measurements.date, Measurements.prcp)\
        .filter(Measurements.date >= start_date)\
        .all()
    prcp_dict = {date: prcp for date, prcp in results}
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Stations.station).all()
    station_list = [station[0] for station in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Find most active station
    most_active = session.query(Measurements.station, func.count(Measurements.id))\
        .group_by(Measurements.station)\
        .order_by(func.count(Measurements.id).desc())\
        .first()[0]

    latest_date = session.query(func.max(Measurements.date)).scalar()
    start_date = dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)

    results = session.query(Measurements.date, Measurements.tobs)\
        .filter(Measurements.station == most_active)\
        .filter(Measurements.date >= start_date)\
        .all()
    
    temps = [{date: tobs} for date, tobs in results]
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    sel = [func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)]

    if not end:
        results = session.query(*sel).filter(Measurements.date >= start).all()
    else:
        results = session.query(*sel).filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    
    temps = {
        "TMIN": results[0][0],
        "TAVG": round(results[0][1], 1),
        "TMAX": results[0][2]
    }
    return jsonify(temps)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
