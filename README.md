# TP-REST Microservices

This project consists of four REST microservices developed with Python and Flask, orchestrated using Docker Compose.

## Running the project

Make sure Docker is installed and running.

From the project root directory, run:

```bash
docker compose up
```

To stop the services:

```bash
docker compose down
```

## Microservices

| Service | Port | Description |
|---|---|---|
| Movie | 3200 | Manages movie information |
| Booking | 3201 | Manages user bookings |
| Schedule | 3202 | Manages movie schedules |
| User | 3203 | Manages users and JWT authentication |

All services are accessible through `http://localhost:<port>`.

## Authentication

Protected endpoints require a JWT token, which can be obtained through:

`POST http://localhost:3203/login`

The token must be included in the request headers:

```http
Authorization: Bearer <token>
```

## Technologies

- Python / Flask
- REST APIs
- JWT Authentication
- Docker / Docker Compose
- JSON files for data storage


