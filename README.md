# ShopSmart E-commerce Platform

A full-stack e-commerce platform with a FastAPI backend and React frontend.

## Features

### Backend

- **User Management**: Authentication, authorization, user profiles
- **Product Catalog**: Categories, products, attributes, variants
- **Inventory Management**: Stock tracking, alerts
- **Order Processing**: Cart, checkout, orders, payments
- **Search & Filtering**: Product search, filters
- **Reviews & Ratings**: Customer feedback
- **Promotions & Discounts**: Coupons, sales, special offers

### Frontend

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Product Browsing**: Browse products by category, brand, or search
- **Product Details**: View detailed product information, images, and variants
- **Shopping Cart**: Add products to cart, update quantities, and remove items
- **Checkout Process**: Complete purchases with shipping and payment information
- **User Authentication**: Register, login, and manage user profile
- **Order Management**: View order history and details
- **Wishlist**: Save products for later

## Tech Stack

### Backend

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

### Frontend

- **Framework**: React
- **State Management**: Redux
- **Routing**: React Router
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form
- **Validation**: Zod
- **Type Safety**: TypeScript
- **Build Tool**: Vite

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
├── frontend/                   # React frontend
│   ├── public/                 # Static files
│   ├── src/                    # Source code
│   │   ├── components/         # React components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── store/              # Redux store
│   │   ├── types/              # TypeScript types
│   │   └── utils/              # Utility functions
│   ├── package.json            # Frontend dependencies
│   └── vite.config.ts          # Vite configuration
├── tests/                      # Backend tests
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
- Node.js 16+ (for frontend development)

### Backend Installation

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

### Frontend Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. The frontend will be available at http://localhost:3000

### API Documentation

Once the application is running, you can access:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Development

### Running Backend Tests

```bash
docker-compose exec api pytest
```

### Adding Database Migrations

After changing models:

```bash
docker-compose exec api alembic revision --autogenerate -m "description"
docker-compose exec api alembic upgrade head
```

### Building Frontend for Production

```bash
cd frontend
npm run build
```

## Deployment

For production deployment, update the environment variables and deploy using Docker Compose or Kubernetes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
