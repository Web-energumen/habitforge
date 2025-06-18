# Habit Tracker API

## Project Overview

A Django REST Framework-based API that allows users to track and analyze their habits over time. Designed to help users
build consistent routines, the app records daily completions of habits and provides analytical insights into
performance.

## Features

- **User Authentication**: Secure registration and login with JWT tokens.
- **Habit Management**:
    - Create, update, and delete personal habits.
    - Each habit is linked to the authenticated user.
- **Daily Habit Recording**:
    - Mark habits as completed on specific dates.
    - Track completions by day for consistent habit maintenance.
- **Habit Analytics**:
    - View daily completion counts aggregated by date.
    - Filter analytics by custom date ranges.
- **Filter & Query Support**:
    - Filter habit records using date ranges.
    - Analytics supports flexible time intervals.
- **Admin Panel:**: Django admin enabled for managing users and habits.

## Technologies Used

- Django: Web framework for building the app.
- Django REST Framework: For building RESTful APIs.
- Simple JWT: JSON Web Token authentication.
- PostgreSQL: Primary database.
- Celery + Redis: Background tasks and scheduling.
- Docker + docker-compose: Containerized development and deployment.
- Nginx: Reverse proxy server.
- GitHub Actions: CI for linting and testing.

## API Usage

### Base URL

`http://localhost:8000/api/`

### Authentication Endpoints

| Endpoint                                 | Method | Description                         |
|------------------------------------------|--------|-------------------------------------|
| /auth/register/                          | POST   | Register a new user                 |
| /auth/verify-email/`<uidb64>`/`<token>`/ | GET    | Verify user email                   |
| /auth/token/                             | POST   | Obtain JWT access and refresh token |
| /auth/token/refresh/                     | POST   | Refresh access token                |
| /auth/token/verify/                      | POST   | Verify validity of a token          |

### Habit Endpoints

| Endpoint            | Method | Description      |
|---------------------|--------|------------------|
| /habits/            | GET    | List user habits |
| /habits/            | POST   | Create new habit |
| /habits/<habit_id>/ | GET    | Retrieve a habit |
| /habits/<habit_id>/ | PUT    | Update a habit   |
| /habits/<habit_id>/ | DELETE | Delete a habit   |

### Habit Records

| Endpoint                           | Method | Description                      |
|------------------------------------|--------|----------------------------------|
| /habits/<habit_pk>/records/        | GET    | List records for a habit         |
| /habits/<habit_pk>/records/        | POST   | Create record for a day          |
| /habits/<habit_pk>/records/`<pk>`/ | GET    | Retrieve a specific habit record |
| /habits/<habit_pk>/records/`<pk>`/ | DELETE | Delete a specific habit record   |

### Habit Schedule Endpoints

| Endpoint                             | 	Method | 	Description                       |
|--------------------------------------|---------|------------------------------------|
| /habits/<habit_pk>/schedule/	        | GET     | 	List schedules for a habit        |
| /habits/<habit_pk>/schedule/	        | POST    | 	Create a new schedule for a habit |
| /habits/<habit_pk>/schedule/`<pk>`/	 | GET     | 	Retrieve a specific schedule      |
| /habits/<habit_pk>/schedule/`<pk>`/	 | PUT     | 	Update a specific schedule        |
| /habits/<habit_pk>/schedule/`<pk>`/	 | DELETE  | 	Delete a specific schedule        |

### Analytics Endpoints

| Endpoint                      | Method | Description                                                                                                 |
|-------------------------------|--------|-------------------------------------------------------------------------------------------------------------|
| /habits/<habit_pk>/analytics/ | GET    | Get daily completion count by date for a habit (supports filtering by start_date and end_date query params) |

### Notes on Filters:

Filter parameters supported for analytics and records:

- start_date — filter records/analytics from this date (YYYY-MM-DD)
- end_date — filter records/analytics up to this date (YYYY-MM-DD)

## Installation

### Prerequisites

- Docker

### Steps to Run the Project

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker
```

2. **Copy the sample environment file and fill it in**:

```bash
cp .env.example .env
```

3. **Start all services**:

```bash
docker compose up --build
```

4. **Apply migrations**:

```bash
docker compose exec web python manage.py migrate
```

5. **Run all tests**:

```bash
docker compose exec web python manage.py test
```

6. **Test the API**:

```bash
curl -X POST http://127.0.0.1/api/auth/register/ \
-H "Content-Type: application/json" \
-d '{
        "username": "testuser",
        "email": "test@example.com",
        "password": "YourStrongPassword123"
    }'
```