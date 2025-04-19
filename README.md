# E-commerce API Backend

A production-ready RESTful API backend for e-commerce applications built with FastAPI and PostgreSQL.

## Features

- **User Management**: Authentication, authorization, user profiles
- **Product Catalog**: Categories, products, attributes, variants
- **Inventory Management**: Stock tracking, alerts
- **Order Processing**: Cart, checkout, orders, payments
- **Search & Filtering**: Product search, filters
- **Reviews & Ratings**: Customer feedback
- **Promotions & Discounts**: Coupons, sales, special offers

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT + OAuth2
- **API Documentation**: Swagger/OpenAPI
- **Testing**: Pytest
- **Deployment**: Docker + Kubernetes
- **CI/CD**: GitHub Actions
- **Caching**: Redis
- **Payment Integration**: Stripe, PayPal

## Project Structure

```
ecommerce_api/
├── alembic/                    # Database migrations
├── app/
│   ├── api/                    # API endpoints
│   ├── core/                   # Core functionality
│   ├── db/                     # Database
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic
│   ├── repositories/           # Data access
│   ├── utils/                  # Utility functions
│   ├── tasks/                  # Background tasks
│   └── main.py                 # FastAPI application
├── tests/                      # Tests
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose
├── alembic.ini                 # Alembic configuration
└── README.md                   # Project documentation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/indranandjha1993/ecommerce_api.git
   cd ecommerce-api
   ```

2. Create a `.env` file with your configuration (see `.env.example`).

3. Build and start the application:
   ```bash
   docker-compose up -d
   ```

4. Run database migrations:
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. Create a superuser:
   ```bash
   docker-compose exec api python -m app.initial_data
   ```

### API Documentation

Once the application is running, you can access:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Development

### Running Tests

```bash
docker-compose exec api pytest
```

### Adding Database Migrations

After changing models:

```bash
docker-compose exec api alembic revision --autogenerate -m "description"
docker-compose exec api alembic upgrade head
```

## Deployment

For production deployment, update the environment variables and deploy using Docker Compose or Kubernetes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
