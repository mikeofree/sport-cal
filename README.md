# sport-cal
 
A simple Flask service that serves sports schedules as `.ics` calendar feeds. Works with Homepage, Google Calendar, or anything that supports iCal.
 
Supports NFL, NBA, and MLB via ESPN's public API.
 
<img width="620" height="832" alt="cal_ics" src="https://github.com/user-attachments/assets/51859f6e-4a9e-4ad5-bf60-305bb0389f29" />
---
 
## Setup
 
```yaml
services:
  sports-ics:
    image: python:3.12-slim
    container_name: sports-ics
    working_dir: /app
    volumes:
      - ./:/app
    ports:
      - "5000:5000"
    command: bash -c "pip install -r requirements.txt && python sports_ics.py"
    restart: unless-stopped
```
 
---
 
## Endpoints
 
| Endpoint   | Description              |
|------------|--------------------------|
| `/nfl.ics` | NFL schedule             |
| `/nba.ics` | NBA schedule             |
| `/mlb.ics` | MLB schedule             |
| `/`        | Lists available feeds    |
 
```
http://<host>:5000/nfl.ics
http://<host>:5000/nba.ics
http://<host>:5000/mlb.ics
```
 
---
 
## Homepage Integration
 
```yaml
- Calendar:
    widget:
      type: calendar
      view: monthly
      timezone: America/Los_Angeles
      integrations:
        - type: ical
          url: http://<host>:5000/nba.ics
          name: NBA
          color: fuchsia
        - type: ical
          url: http://<host>:5000/mlb.ics
          name: MLB
          color: indigo
        - type: ical
          url: http://<host>:5000/nfl.ics
          name: NFL
          color: indigo
```
 
---
 
## How It Works
 
Fetches team schedules from ESPN's public API, deduplicates games, and serves them as `.ics` feeds. Events are prefixed with the league name (e.g. `MLB: Yankees @ Red Sox`). Schedules are cached in memory for 24 hours.
 
---
 
## Requirements
 
```
flask
icalendar
requests
```
 
---
 
## License
 
MIT
 
