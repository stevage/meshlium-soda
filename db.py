'''
Aggregate Meshlium sensor readings from a database.

Author: Steve Bennett, stevage@gmail.com
Licence: WTFPL
'''


from sqlalchemy import *
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
import sqlalchemy, re
import config

db_uri = 'mysql://%s:%s@%s:%s/%s' % (config.SQL_USER, config.SQL_PASSWORD, config.SQL_IP, config.SQL_PORT, config.SQL_DB)
DEBUGSQL = False
db = sqlalchemy.create_engine(db_uri, encoding='latin1', echo=DEBUGSQL)


'''
Run aggregation query on the database and return results as a dict.
latest_published: string timestamp, only data newer than this will be returned
rowlimit: only this number of records will be returned.
'''
def getReadings(latest_published, rowlimit):
  interval_mins = 5 # Period in minutes over which to aggregate readings.
  aggregate_environmental = '''SELECT
      date_sub(timestamp,interval (minute(timestamp) %% %d ) * 60 + second(timestamp) second) AS timestamp_agg,
      si.boardid, 
      si.boardtype, 
      sr.mac,
      convert(avg(convert(temperature, decimal(5,1))),decimal(5,1)) AS temp_avg,
      min(convert(temperature, decimal(5,1))) AS temp_min,
      max(convert(temperature, decimal(5,1))) as temp_max,
      convert(avg(convert(light, decimal(5,1))),decimal(5,1)) AS light_avg,
      min(convert(light, decimal(5,1))) AS light_min,
      max(convert(light, decimal(5,1))) as light_max,
      convert(avg(convert(humidity, decimal(5,1))),decimal(5,1)) AS humidity_avg,
      min(convert(humidity, decimal(5,1))) AS humidity_min,
      max(convert(humidity, decimal(5,1))) as humidity_max,
      lat,
      lon,
      eln,
      max(location) AS location,
      max(model) AS model
      FROM sensorReadings sr 
      INNER JOIN sensor_info si on si.boardid = sr.boardid
      WHERE temperature <> '' 
      GROUP BY sr.boardid, date_sub(timestamp,interval (minute(timestamp) %% %d) * 60  + second(timestamp) second)
      HAVING timestamp_agg > '%s'
      ORDER BY timestamp
      LIMIT %d''' % (interval_mins, interval_mins, latest_published, rowlimit) # No idea why normal :parameters don't work.



  rows = []
  d = db.execute(text(aggregate_environmental)).fetchall()
  # There's probably a smarter way of doing all this.

  #TODO: Need to support timezone. We want to store the data in the portal as timezone-included Melbourne time,
  # but in the database as timezone-not-included UTC.

  for r in d:
    rowid = str(r['boardid']) + '-' + re.sub('[-: ]', '', str(r['timestamp_agg']))
    #print str(r['timestamp_agg'])
    row = {
      'rowid': rowid,
      'temp_max': r['temp_max'],
      'temp_min': r['temp_min'],
      'temp_avg': r['temp_avg'],
      'timestamp': str(r['timestamp_agg']),
      'light_max': r['light_max'],
      'light_min': r['light_min'],
      'light_avg': r['light_avg'],
      'humidity_max': r['humidity_max'],
      'humidity_min': r['humidity_min'],
      'humidity_avg': r['humidity_avg'],
      'boardtype': r['boardtype'],
      'boardid': r['boardid'],
      'latitude': r['lat'],
      'longitude': r['lon'],
      'elevation': r['eln'],
      'location': r['location'],
      'model': r['model'],
      'mac': r['mac']      

    }
    rows.append(row)

  return rows


'''
Get just the sensor information
'''
def getLocations():
  getSensorInfo = '''SELECT boardid, boardtype, model, lat, lon, eln, location 
    FROM sensor_info
    '''

  d = db.execute(text(getSensorInfo)).fetchall()
  rows = []
  for r in d:
    row = {
      'boardid': r['boardid'],
      'boardtype': r['boardtype'],
      'model': r['model'],
      'latitude': r['lat'],
      'longitude': r['lon'],
      'elevation': r['eln'],
      'location': r['location']

    }
    rows.append(row)

  return rows