# Import dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt

# Database setup
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/hawaii"  # Update with your PostgreSQL credentials
engine = create_engine(DATABASE_URL)
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
try:
    Measurement = Base.classes.measurement  # Ensure this matches the actual table name
    Station = Base.classes.station  # Ensure this matches the actual table name
except KeyError as e:
    print(f"Error: Table {e} not found. Please ensure the table exists in the database.")
    exit(1)

# Flask app setup
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session
    session = Session(engine)
    
    # Find the most recent date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    # Convert results to a dictionary
    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create a session
    session = Session(engine)
    
    # Query all stations
    results = session.query(Station.station).all()
    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session
    session = Session(engine)
    
    # Find the most recent date in the dataset
    recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Query the last 12 months of temperature observation data for the most-active station
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
    session.close()
    
    # Convert list of tuples into normal list
    tobs_data = list(np.ravel(results))
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):
    # Create a session
    session = Session(engine)
    
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        # Calculate TMIN, TAVG, TMAX for all dates greater than start date
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        # Calculate TMIN, TAVG, TMAX for dates between start and end date inclusive
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    
    # Convert list of tuples into normal list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)
