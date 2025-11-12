# Sports ICS Calendar Generator

This project provides a small Flask-based service that generates `.ics` calendar feeds for sports schedules. It currently supports the NFL and NBA. The feeds can be used with Homepage (gethomepage.dev) or any calendar application that supports the iCal format.

---

## Features

- Generates `.ics` files for NFL and NBA schedules
- Lightweight Flask web service
- Docker-ready using a single `docker-compose.yml`
- In-memory caching to reduce external API calls
- Straightforward endpoint structure for integration

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

---

## Installation and Deployment

Clone the repository:

```bash
git clone https://github.com/mikeofree/sport-cal.git
cd sport-cal
```

Start the container:

```bash
docker compose up -d
```

View logs:

```bash
docker logs -f sports-ics
```

The container exposes port `5000`, mapped to `5000` on the host by default.

---

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

## Roadmap

Planned improvements:

- Additional leagues (NHL, MLB)
- Team-specific feeds (e.g., `/nfl/49ers.ics`)
- Configurable cache refresh interval
- Environment variable settings
- Optional on-disk caching
- Dockerfile and pre-built container publishing
- GitHub Actions workflows for automated builds

Future ideas:

- NCAA schedules
- Optional small web dashboard
- JSON endpoints for raw schedule data

---

## License

This project is licensed under the MIT License.
