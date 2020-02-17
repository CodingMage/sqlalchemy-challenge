import numpy as np 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


###############################################
# app starts here
###############################################

app = Flask(__name__)

# Defining (modifying) calc_temp for arbituary end_date input.
def calc_temps(start_date, end_date=None):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)

    # start_date as the only input.
    if end_date == None:
        data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()
        session.close()
        return data
    
    # Both start and end date was given.
    else:
        data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all() 
        session.close()
        return data


@app.route('/')
def home():
    """List all variable api routes"""
    print('Home page accessed from user.')
    return (
        f'Available Routes:<br>'
        f'/api/v1.0/precipitation<br>'
        f'/api/v1.0/stations<br>'
        f'/api/v1.0/tobs<br>'
        f'/api/v1.0/&ltstartdate&gt<br>'
        f'/api/v1.0/&ltstartdate&gt/&ltenddate&gt<br>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return a dictionary using date as the key and prcp as the value."""
    
    print('accessing the prcp data')

    # Create session and making queries.
    session = Session(engine)
    prcp_data = session.query(Measurement.date, func.max(Measurement.prcp))\
                .filter(Measurement.date >= '2016-08-23')\
                .group_by(Measurement.date)\
                .order_by(Measurement.date).all()
    session.close()

    # Saving the query results as dictionary.
    # dates = list()
    # precipitation = list()
    results = dict()
    for each in prcp_data:
        
        if each[1] == None or each[1] == 0.00:
            pass
        else:
            results[each[0]] = each[1]
            # dates.append(each[0])
            # precipitation.append(each[1])

    return jsonify(results)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    station = session.query(Measurement.station)\
                     .group_by(Measurement.station).all()
    session.close()

    list_of_station = list(np.ravel(station))

    return jsonify(list_of_station)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    tob_query = session.query(Measurement.date, Measurement.tobs)\
                   .filter(Measurement.station == 'USC00519281')\
                   .filter(Measurement.date >= '2016-08-18').all()
    session.close()

    tobs = dict()
    for each in tob_query:
        tobs[each[0]] = each[1]

    return jsonify(tobs)

@app.route('/api/v1.0/<startdate>')
def start_data(startdate):
    
    session = Session(engine)
    
    # Calling calc_temps defined above, convert into list and pass to certain variables.
    TMIN, TAVG, TMAX = list(np.ravel(calc_temps(startdate)))
    session.close()
    data = dict()
    data['TMIN'] = TMIN
    data['TAVG'] = TAVG
    data['TMAX'] = TMAX

    return jsonify(data)


@app.route('/api/v1.0/<startdate>/<enddate>')
def start_end_data(startdate, enddate):

    session = Session(engine)
    TMIN, TAVG, TMAX = list(np.ravel(calc_temps(startdate, enddate)))
    session.close()

    data = dict()
    data['TMIN'] = TMIN
    data['TAVG'] = TAVG
    data['TMAX'] = TMAX

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
    