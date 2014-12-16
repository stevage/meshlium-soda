Publish aggregated Meshlium sensor readings to a SODA API such as Socrata.
Created for a City of Melbourne/University of Melbourne project as Data Guru in Residence.

Author: Steve Bennett, stevage@gmail.com

Licence: WTFPL

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
python publish.py
```
