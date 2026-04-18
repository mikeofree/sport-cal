# Sports ICS Calendar Generator
 
This project provides a small Flask-based service that generates `.ics` calendar feeds for sports schedules. It currently supports the NFL, NBA, and MLB. The feeds can be used with Homepage (gethomepage.dev) or any calendar application that supports the iCal format.
 
---
 
## Features
 
- Generates `.ics` files for NFL, NBA, and MLB schedules
- League prefix included in event titles (e.g. `MLB: Kansas City Royals @ New York Yankees`)
- Lightweight Flask web service
- Docker-ready using a single `docker-compose.yml`
- In-memory caching to reduce external API calls
- Straightforward endpoint structure for integration
<img width="620" height="832" alt="cal_ics" src="https://github.com/user-attachments/assets/51859f6e-4a9e-4ad5-bf60-305bb0389f29" />
---
 
## Project Structure
 
```
sport-cal/
│
├── sports_ics.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```
 
## Docker Compose Example
 
```yaml
services:
  sports-ics:
    image: python:3.12
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
 
## API Endpoints
 
| Endpoint   | Description                           |
|------------|---------------------------------------|
| `/nfl.ics` | Returns the NFL schedule as an ICS    |
| `/nba.ics` | Returns the NBA schedule as an ICS    |
| `/mlb.ics` | Returns the MLB schedule as an ICS    |
| `/`        | Health check / lists available feeds  |
 
Example:
 
```
http://<host>:5000/nfl.ics
http://<host>:5000/nba.ics
http://<host>:5000/mlb.ics
```
 
These URLs can be used with Homepage or any calendar application that supports `.ics`.
 
> **Note:** The NFL feed will return no events during the offseason (roughly February–August) and may show an error in Homepage during that period. Simply comment it out until preseason schedules are published.
 
---
 
## Homepage Integration Example
 
Example configuration for the Homepage `calendar` widget:
 
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
        # Uncomment during NFL season (September - February):
        # - type: ical
        #   url: http://<host>:5000/nfl.ics
        #   name: NFL
        #   color: indigo
```
 
---
 
## Running Without Docker
 
Install dependencies:
 
```bash
pip install -r requirements.txt
```
 
Start the server:
 
```bash
python sports_ics.py
```
 
---
 
## Requirements
 
```
flask
icalendar
requests
```
 
---
 
## How It Works
 
- The Flask server provides routes for each league.
- When an `.ics` file is requested, the service retrieves schedule data from ESPN's public API.
- All team schedules are fetched and deduplicated so each game appears only once.
- Events are formatted with a league prefix (e.g. `NBA:`, `MLB:`) for easy identification in calendar views.
- Data is cached in memory for 24 hours to reduce repeat external requests.
- The resulting `.ics` file can be imported into any compatible calendar application.
---
 
## License
 
This project is licensed under the MIT License.
