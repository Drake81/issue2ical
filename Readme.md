# Issue2ical

Generates an ical calendar from given gitlab repository including every milestone and every issue, which does have a due date.

## Setup

* Clone repository
* Change into repository
* Create virtualenv for python 3.4, activate it and install packages

```sh
virtualenv -p /usr/bin/python3.4 venv
source venv/bin/activate
pip install -r requirements.txt
```

* Copy config file and fit to your needs

```sh
cp settings.example.py settings.py
```

## Run script

```sh
source venv/bin/activate
python issue2ical.py
```