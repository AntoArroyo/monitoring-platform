# Raspberry Pi Monitoring Platform

A containerized system monitoring platform built with FastAPI,
PostgreSQL, and Chart.js.\
The application collects system metrics from a Raspberry Pi and presents
them in a responsive web dashboard with real-time updates.

------------------------------------------------------------------------

## Overview

This project provides:

-   Real-time monitoring of CPU, RAM, Disk usage, and Raspberry Pi
    temperature
-   Historical time-series visualization (last 60 minutes)
-   REST API built with FastAPI
-   PostgreSQL database for metric storage
-   Docker-based development and deployment
-   Automated test setup using Pytest

The dashboard is responsive and designed to run on desktop browsers,
tablets, or Raspberry Pi touchscreens.


------------------------------------------------------------------------

## Running with Docker

Build and start the application:

``` bash
docker compose build
docker compose up
```

API:

``` text
http://localhost:8000
```

Dashboard:

``` text
http://localhost:8000/dashboard
```

------------------------------------------------------------------------

## Run agent on a Raspberry Pi
To run the agent on a Raspberry Pi, build the agent

``` bash
cargo run -- --server-url http://localhost:8000 --agent-id <your-agent-id>

```


------------------------------------------------------------------------


## Testing

Run the test suite with:

``` bash
pytest
```

Tests use an isolated SQLite database and override application
dependencies to ensure separation from production data.

