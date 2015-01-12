Publish aggregated Meshlium sensor readings from a MySQL database to a SODA API such as Socrata.
Created for a City of Melbourne/University of Melbourne project as Data Guru in Residence.

Author: Steve Bennett, stevage@gmail.com

Licence: Dual licensed, BSD 3 and "Go nuts". (See LICENSE.md)

## Installation

Built with Python 2.8

```
sudo apt-get install -y python-pip python-mysqldb
sudo pip install sqlalchemy mysql-python simplejson
cp config_changeme.py config.py
```

Now edit `config.py` to set app token, usernames and passwords.

## Run
```
python publish.py --help

usage: publish.py [-h] [--wipe] [--verbose] [--rows ROWS]

Aggregate Meshlium data and send to Socrata.

optional arguments:
  -h, --help   show this help message and exit
  --wipe       First wipe all rows from the destination.
  --verbose    Produce verbose output for debugging
  --rows ROWS  Number of rows to send.
```
