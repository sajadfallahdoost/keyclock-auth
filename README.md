# FastAPI Keycloak Authentication Project

A comprehensive FastAPI application with Keycloak authentication integration, featuring user management, products, and orders modules.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Keycloak Integration** - Complete authentication and authorization system
- **PostgreSQL Database** - Robust relational database support
- **Alembic Migrations** - Database version control
- **Docker Support** - Easy deployment with Docker Compose
- **Modular Architecture** - Well-organized codebase with separate modules
- **JWT Authentication** - Secure token-based authentication
- **Role-Based Access Control (RBAC)** - Fine-grained permission system

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.12 or higher
- **Docker** and **Docker Compose** (for containerized setup)
- **PostgreSQL** (if running locally without Docker)
- **Git**

## 🛠️ Installation & Setup

### Option 1: Using Docker Compose (Recommended)

This is the easiest way to get started. Docker Compose will set up both Keycloak and the FastAPI application.

1. **Clone the repository**
   ```bash
   git clone https://github.com/sajadfallahdoost/keyclock-auth.git
   cd keyclock-auth
   ```

2. **Create a `.env` file** (if it doesn't exist)
   ```bash
   # Keycloak Configuration
   KEYCLOAK_ADMIN_USERNAME=admin
   KEYCLOAK_ADMIN_PASSWORD=admin
   KEYCLOAK_REALM=master
   KEYCLOAK_CLIENT_ID=backend-service
   KEYCLOAK_ADMIN_REALM=master
   KEYCLOAK_ADMIN_CLIENT_ID=admin-cli
   
   # Service Account
   SERVICE_USERNAME=service-user
   SERVICE_PASSWORD=service-pass
   
   # Database Configuration (if using external database)
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

   This will:
   - Start Keycloak on `http://localhost:8080`
   - Start the FastAPI application on `http://localhost:8000`
   - Set up all necessary networking between services

4. **Access the services**
   - **FastAPI API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Keycloak Admin Console**: http://localhost:8080
     - Username: `admin` (or your `KEYCLOAK_ADMIN_USERNAME`)
     - Password: `admin` (or your `KEYCLOAK_ADMIN_PASSWORD`)

5. **Stop the services**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development Setup

If you prefer to run the application locally without Docker:

1. **Clone the repository**
   ```bash
   git clone https://github.com/sajadfallahdoost/keyclock-auth.git
   cd keyclock-auth
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   KEYCLOAK_SERVER_URL=http://localhost:8080
   KEYCLOAK_REALM=master
   KEYCLOAK_CLIENT_ID=backend-service
   KEYCLOAK_ADMIN_REALM=master
   KEYCLOAK_ADMIN_CLIENT_ID=admin-cli
   KEYCLOAK_ADMIN_USERNAME=admin
   KEYCLOAK_ADMIN_PASSWORD=admin
   SERVICE_USERNAME=service-user
   SERVICE_PASSWORD=service-pass
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

5. **Set up Keycloak**
   
   You need to have Keycloak running. You can either:
   - Use Docker: `docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:latest start-dev`
   - Install Keycloak locally and run it

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the FastAPI application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

### Keycloak Setup

After starting Keycloak, you need to configure it:

1. **Access Keycloak Admin Console**
   - URL: http://localhost:8080
   - Login with admin credentials

2. **Create a Client**
   - Go to **Clients** → **Create client**
   - Client ID: `backend-service` (or match your `KEYCLOAK_CLIENT_ID`)
   - Client protocol: `openid-connect`
   - Access Type: `confidential` or `public` (depending on your needs)
   - Valid Redirect URIs: `http://localhost:8000/*`
   - Web Origins: `http://localhost:8000`

3. **Create Users and Roles**
   - Go to **Users** → **Add user**
   - Set username, email, and password
   - Go to **Roles** to create roles (e.g., `admin`, `user`)
   - Assign roles to users in the **Role Mappings** tab

## 📚 API Endpoints

### Public Endpoints

- `GET /` - Home endpoint with project information
- `GET /docs` - Swagger UI documentation
- `GET /openapi.json` - OpenAPI schema

### Protected Endpoints

- `GET /me` - Get current user profile (requires authentication)
- `GET /admin` - Admin-only endpoint (requires `admin` role)
- `GET /service-data` - Service account endpoint

### Module Endpoints

The application includes modules for:
- **Users** (`/api/v1/users/`)
- **Products** (`/modules/products/`)
- **Orders** (`/modules/orders/`)

## 🧪 Testing

Run the test suite:

```bash
pytest
```

For verbose output:

```bash
pytest -v
```

## 📁 Project Structure

```
keyclock-auth/
├── api/                    # API routes and endpoints
│   ├── v1/                 # API version 1
│   └── healthcheck.py      # Health check endpoint
├── app/
│   ├── core/               # Core application logic
│   │   ├── config.py       # Configuration settings
│   │   ├── security.py     # Authentication & authorization
│   │   └── dependencies.py # FastAPI dependencies
│   └── services/           # Business logic services
│       └── keycloak_admin.py
├── conf/                   # Configuration files
│   ├── database/           # Database configuration
│   ├── alembic/            # Database migrations
│   ├── redis/              # Redis client
│   └── rabbit/             # RabbitMQ connection
├── modules/                # Feature modules
│   ├── users/              # User management
│   ├── products/           # Product management
│   └── orders/             # Order management
├── tests/                  # Test files
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── alembic.ini             # Alembic configuration
```

## 🔐 Authentication Flow

1. **User Login**: User authenticates with Keycloak
2. **Token Generation**: Keycloak issues a JWT token
3. **API Request**: Client includes token in `Authorization: Bearer <token>` header
4. **Token Validation**: FastAPI validates token against Keycloak's JWKS endpoint
5. **Authorization**: Role-based access control is enforced

## 🐳 Docker Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View running containers
docker-compose ps
```

## 🗄️ Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migration:

```bash
alembic downgrade -1
```

## 🔍 Troubleshooting

### Keycloak Connection Issues

- Ensure Keycloak is running and accessible
- Check `KEYCLOAK_SERVER_URL` in your `.env` file
- Verify network connectivity between services

### Database Connection Issues

- Verify PostgreSQL is running
- Check `DATABASE_URL` in your `.env` file
- Ensure database credentials are correct

### Authentication Failures

- Verify client configuration in Keycloak
- Check token expiration
- Ensure roles are properly assigned in Keycloak

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KEYCLOAK_SERVER_URL` | Keycloak server URL | `http://localhost:8080` |
| `KEYCLOAK_REALM` | Keycloak realm name | `master` |
| `KEYCLOAK_CLIENT_ID` | Keycloak client ID | `backend-service` |
| `KEYCLOAK_ADMIN_USERNAME` | Keycloak admin username | `admin` |
| `KEYCLOAK_ADMIN_PASSWORD` | Keycloak admin password | `admin` |
| `SERVICE_USERNAME` | Service account username | `service-user` |
| `SERVICE_PASSWORD` | Service account password | `service-pass` |
| `DATABASE_URL` | PostgreSQL connection string | - |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Sajad Fallahdoost**

- GitHub: [@sajadfallahdoost](https://github.com/sajadfallahdoost)

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- Keycloak project for robust authentication
- All contributors and users of this project

---

**Happy Coding! 🚀**

