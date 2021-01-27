import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
        
    )

    
@app.route("/api/v1.0/precipitation") 
def precipitation():
	session = Session(engine)
   
	results = session.query(measurement.date, measurement.prcp).all()

	session.close()

	prec_dict = []
	for date, prcp in results:
		precip = {}
		precip["date"] = date
		precip["prcp"] = prcp
		prec_dict.append(precip)

	return jsonify(prec_dict)

@app.route("/api/v1.0/stations")
def stations():
	session = Session(engine)

	results = session.query(station.station).all()

	session.close()


	all_stations = list(np.ravel(results))

	return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
	session = Session(engine)
   
	results = session.query(measurement.date, measurement.tobs, measurement.station).all()

	session.close()

	activestation = session.query(measurement.station, measurement.id).group_by(measurement.station).order_by(-measurement.id).all()
	most_active_station = (activestation[0])[0]

	temps = []
	for date, tobs, station in results:
		temp_dict = {}
		temp_dict["date"] = date
		temp_dict["tobs"] = tobs
		if station == most_active_station:
			temps.append(temp_dict)

	return jsonify(temps)

@app.route("/api/v1.0/<start>")
def start_date(start):
	session = Session(engine)
   
	results = session.query(measurement.date, measurement.tobs, measurement.station).all()

	session.close()

	sel = [measurement.date, func.avg(measurement.tobs), func.min(measurement.tobs), func.max(measurement.tobs)]
	results = session.query(*sel).filter(measurement.date >= start).order_by(measurement.tobs).all()
	average = (results[0])[1]
	low = (results[0])[2]
	high = (results[0])[3]

	stats = []
	# stats.append(average)
	# stats.append(low)
	# stats.append(high)

	# return("Temps are: Average: "+ str(average)+", Low: "+str(low)+", High: "+str(high) 
	# )

	temp_dict = {}
	temp_dict["TMIN"] = low
	temp_dict["TAVG"] = average
	temp_dict["TMAX"] = high
	stats.append(temp_dict)

	return jsonify(stats)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start=None, end=None):
	session = Session(engine)
   
	results = session.query(measurement.date, measurement.tobs, measurement.station).all()

	session.close()

	sel = [measurement.date, func.avg(measurement.tobs), func.min(measurement.tobs), func.max(measurement.tobs)]
	results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).order_by(measurement.tobs).all()
	average = (results[0])[1]
	low = (results[0])[2]
	high = (results[0])[3]
	
	stats = []
	# stats.append(average)
	# stats.append(low)
	# stats.append(high)

	# return("Temps are: Average: "+ str(average)+", Low: "+str(low)+", High: "+str(high) 
	# )

	temp_dict = {}
	temp_dict["TMIN"] = low
	temp_dict["TAVG"] = average
	temp_dict["TMAX"] = high
	stats.append(temp_dict)

	return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True)