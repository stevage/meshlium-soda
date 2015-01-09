#!/usr/bin/env python 
'''
Publish aggregated Meshlium sensor readings to a SODA API such as Socrata.
Created for a City of Melbourne/University of Melbourne project as Data Guru in Residence.

Author: Steve Bennett, stevage@gmail.com
Licence: WTFPL
'''

import requests, logging, simplejson, argparse, datetime
import config
import db
headers = {'X-App-Token': config.app_token}
headers['Content-Type'] = 'application/json'

def getArgs():
  p = argparse.ArgumentParser(description='Aggregate Meshlium data and send to Socrata.')
  p.add_argument('--wipe', help='First wipe all rows from the destination.', action='store_true')
  p.add_argument('--rows', help='Number of rows to send.', type=int, default=2)
  return p.parse_args()


'''
Delete all rows in portal. There's no other way to do this than through the API.
'''
def deleteAll():
  r = requests.put(config.dataset + '.json', data='[ ]', headers=headers, auth=config.auth)
  print r.status_code, r.text

'''
Query portal to find most recent timestamp already present
'''
def latestPublished():
  from time import strftime, strptime
  
  params = {#'$select': 'max(timestamp)',
            '$limit': 1, 
            '$order': 'timestamp DESC',
            '$where': 'timestamp IS NOT NULL'}
  r = requests.get(config.dataset + '.json', params=params, headers=headers, auth=config.auth)
  if r.status_code != 200:
    raise RuntimeError('Can''t retrieve latest timestamp.' + r.text)
  if len(r.json()) == 0:
    return '2014-12-14'
  # Sometimes we need to convert from "03/12/2014 09:56" to "2014-12-03 09:56:00". Why? I don't know.
  t = r.json()[0]['timestamp']
  if t.find("/") > 0:
    t = strftime("%Y-%m-%d %H:%M:%S", strptime(t,  "%d/%m/%Y %H:%M"))
  return t

'''
Query portal to find out how many rows are already published
'''
def rowsPublished():
  params = {'$select': 'count(*)'}
  r = requests.get(config.dataset + '.json', params=params, headers=headers, auth=config.auth)
  if r.status_code != 200:
    raise RuntimeError('Can''t retrieve row count.' + r.text)
  if len(r.json()) == 0:
    return 0
  count = int(r.json()[0]['count'])
  return count

def publishDataset(rows):
  print simplejson.dumps(rows)
  r = requests.post(config.dataset, data=simplejson.dumps(rows), headers = headers, auth=config.auth)
  j = r.json()
  print
  if r.status_code != 200:
    raise RuntimeError ( "%d Socrata error: %s" % (r.status_code, j['message']))
  return j

# Main:
args = getArgs()
if args.wipe:
  latest_published = latestPublished()
  print 'Latest timestamp: %s (%d rows)' % (latest_published, rowsPublished())
  if raw_input("Wipe all data in portal? Type WIPE to confirm: ") == "WIPE":
    deleteAll()
  else:
    print "Aborting."
    quit()
  
print "(For usage: publish.py --help)"
print "Publishing up to %d rows now: %s" % (args.rows, datetime.datetime.now())
latest_published = latestPublished()
print 'Latest timestamp: %s (%d rows)' % (latest_published, rowsPublished())
rows = db.getReadings(latest_published, args.rows)
print "Sending %d rows." % len(rows)
j = publishDataset(rows)

print "Socrata says: %d new rows, %d rows updated." % (j['Rows Created'], j['Rows Updated'])
print 'Latest timestamp now: %s (%d rows)' % ( latestPublished(), rowsPublished())


