'''
Publish aggregated Meshlium sensor readings to a SODA API such as Socrata.
Created for a City of Melbourne/University of Melbourne project as Data Guru in Residence.

Author: Steve Bennett, stevage@gmail.com
Licence: WTFPL
'''

import requests, logging, simplejson
import config
import db
headers = {'X-App-Token': config.app_token}
headers['Content-Type'] = 'application/json'


'''
Delete all rows in portal. There's no other way to do this than through the API.
'''
def deleteAll():
  params = {'$select': 'rowid',
            '$order': 'rowid', 
            '$limit': 100}
  r = requests.get(dataset + '.json', params=params, headers=headers, auth=config.auth)
  count=0
  if r.status_code == requests.codes.ok:
    for row in r.json():
      #print row['rowid']
      d = requests.delete(dataset + '/' + row['rowid'] + '.json', headers=headers, auth=config.auth)
      if d.status_code == 200:
        print '%d Deleted %s: %s' % (d.status_code, row['rowid'], d.request.url)
        count = count + 1
      else:
        print '*** %d Failed to delete %s: %s' % (d.status_code, row['rowid'], d.request.url) 
  print "Deleted %d/%d rows successfully." % (count, len(r.json()))


#deleteAll()
#quit()

'''
Find most recent timestamp already present in portal
'''
def latestPublished():
  from time import strftime, strptime
  
  params = {'$limit': 1, 
            '$order': 'timestamp DESC',
            '$where': 'timestamp IS NOT NULL'}
  r = requests.get(config.dataset + '.json', params=params, headers=headers, auth=config.auth)
  if r.status_code != 200:
    raise RuntimeError('Can''t retrieve latest timestamp.' + r.text)
  if len(r.json()) == 0:
    return '1970-01-01'
  # Sometimes we need to convert from "03/12/2014 09:56" to "2014-12-03 09:56:00". Why? I don't know.
  t = r.json()[0]['timestamp']
  if t.find("/") > 0:
    t = strftime("%Y-%m-%d %H:%M:%S", strptime(t,  "%d/%m/%Y %H:%M"))
  return t
  

latest_published = latestPublished()
print 'Latest timestamp: ' + latest_published
rows = db.getReadings(latest_published, 10)
print "Sending %d rows." % len(rows)
r = requests.post(config.dataset, data=simplejson.dumps(rows), headers = headers, auth=config.auth)
j = r.json()
print
if r.status_code != 200:
  print "%d Socrata error: %s" % (r.status_code, j['message'])
else:
  print "Socrata says: %d new rows, %d rows updated." % (j['Rows Created'], j['Rows Updated'])
  latest_published = latestPublished()
  print 'Latest timestamp now: ' + latest_published


