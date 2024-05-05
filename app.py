# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine, func, Column, Integer, String, Float
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import datetime as dt

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()


Base.prepare(engine, reflect=True)


if 'measurement' not in Base.classes or 'station' not in Base.classes:
    Base = declarative_base()

    class Station(Base):
        __tablename__ = 'station'
        id = Column(Integer, primary_key=True)
        station = Column(String)

    class Measurement(Base):
        __tablename__ = 'measurement'
        id = Column(Integer, primary_key=True)
        station = Column(String)
        date = Column(String)
        prcp = Column(Float)
        tobs = Column(Float)

    # Create tables database
    Base.metadata.create_all(engine)
else:
    Measurement = Base.classes.measurement
    Station = Base.classes.station

# Flask app setup
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    with Session(engine) as session:
        last_date = session.query(func.max(Measurement.date)).scalar()
        one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    with Session(engine) as session:
        results = session.query(Station.station).all()
        all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    with Session(engine) as session:
        most_active_station = 'USC00519281'
        last_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
        one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
        results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()
        tobs_data = list(np.ravel(results))

    return jsonify(tobs_data)

if __name__ == '__main__':
    app.run(debug=True)