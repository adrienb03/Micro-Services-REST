# TP-REST Microservices

This project consists of 4 REST microservices developed with Python and Flask, orchestrated using Docker Compose. Each microservice uses its own MongoDB database.

## Running the project

Make sure Docker is installed and running.

From the project root directory, run:

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

To stop the services and delete the MongoDB data:

```bash
docker compose down -v
```

## Microservices

| Service | Port | Description |
|---|---|---|
| Movie | 3200 | Manages movie information |
| Booking | 3201 | Manages user bookings |
| Schedule | 3202 | Manages movie schedules |
| User | 3203 | Manages users and JWT authentication |
| Mongo Express | 8081 | Web interface for MongoDB |

All REST services are accessible through `http://localhost:<port>`.

Mongo Express is accessible at `http://localhost:8081`.

## Database

The project uses MongoDB with a separate database for each microservice:

| Service | Database |
|---|---|
| Movie | `movies_db` |
| Booking | `bookings_db` |
| Schedule | `schedules_db` |
| User | `users_db` |

The databases are initialized with data from JSON files when their collections are empty.

MongoDB data is stored in a Docker volume (`mongo_data`).

## Authentication

Protected endpoints require a JWT token, which can be obtained through:

`POST http://localhost:3203/login`

The token must be included in the request headers

```http
Authorization: Bearer <token>
```

Some endpoints are restricted to administrators.
