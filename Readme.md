# Issue2ical

Generates an ical calendar for every milestone and every issue, which does have an due date.

## Setup

1. Clone repository
2. Change into repository
3. Create virtualenv for python 3.4, activate it and install packages

```sh
virtualenv -p /usr/bin/python3.4 venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Copy config file and fit to your needs

```sh
cp settings.example.py settings.py
```

5. Execute script

```sh
python issue2ical.py
```