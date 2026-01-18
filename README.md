# Sports ICS Calendar Generator

This project provides a small Flask-based service that generates `.ics` calendar feeds for sports schedules. It currently supports the NFL and NBA. The feeds can be used with Homepage (gethomepage.dev) or any calendar application that supports the iCal format.

---

## Features

- Generates `.ics` files for NFL and NBA schedules
- Lightweight Flask web service
- Docker-ready using a single `docker-compose.yml`
- In-memory caching to reduce external API calls
- Straightforward endpoint structure for integration
<img width="874" height="704" alt="image" src="https://github.com/user-attachments/assets/ce3ba27f-fd84-4b48-9e47-6361032fbb05" />

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
```

---

## API Endpoints

| Endpoint   | Description                           |
|------------|---------------------------------------|
| `/nfl.ics` | Returns the NFL schedule as an ICS    |
| `/nba.ics` | Returns the NBA schedule as an ICS    |
| `/health`  | Basic health-check endpoint           |
| `/refresh` | Optional cache refresh endpoint       |

Example:

```
http://<host>:5000/nfl.ics
http://<host>:5000/nba.ics
```

These URLs can be used with Homepage or any calendar application that supports `.ics`.

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
          url: http://<host>:5000/nfl.ics
          name: NFL
          color: indigo
        - type: ical
          url: http://<host>:5000/nba.ics
          name: NBA
          color: fuchsia
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
- When an `.ics` file is requested, the service retrieves schedule data from a public sports API.
- The data is parsed and converted into iCalendar events using the `icalendar` library.
- A simple in-memory cache reduces repeat external requests.
- The resulting `.ics` file can then be imported into any compatible calendar application.

---

## License

This project is licensed under the MIT License.
