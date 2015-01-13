#!/usr/bin/env python 
'''
Publish locations of Meshlium sensors readings from MySQL to a SODA API such as Socrata.
Created for a City of Melbourne/University of Melbourne project as Data Guru in Residence.

Author: Steve Bennett, 
Web: http://stevebennett.me
Twitter: @stevage1 
Email: stevage@gmail.com 
Tumblr: http://melbdataguru.tumblr.com 
Licence: Go nuts/BSD3 (see LICENSE.md)
'''

import requests, logging, simplejson, argparse, datetime
import config
import db
headers = {
  'X-App-Token': config.app_token,
  'Content-Type': 'application/json'
  }


def publishLocations(rows):

  # Delete all rows first. For simplicity.
  #r = requests.delete(config.locations_dataset + '.json', data='[ ]', headers=headers, auth=config.auth)
  #print "Deleted rows: %d " % r.status_code


  print simplejson.dumps(rows)
  r = requests.post(config.locations_dataset, data=simplejson.dumps(rows), headers = headers, auth=config.auth)
  j = r.json()
  print
  if r.status_code != 200:
    raise RuntimeError ( "%d Socrata error: %s" % (r.status_code, j['message']))
  return j

# Main:
rows = db.getLocations()
print "Sending %d location rows." % len(rows)
j = publishLocations(rows)

print "Socrata says: %d new rows, %d rows updated." % (j['Rows Created'], j['Rows Updated'])


