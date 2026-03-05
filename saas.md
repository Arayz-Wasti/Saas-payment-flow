SaaS Backend: Step-by-Step Implementation Guide
Project Overview
This project follows a modular, phase-based approach to building a production-grade Django SaaS backend with PostgreSQL, Stripe, and JWT authentication.

Development Phases
Phase 1: Project Initialization
Initialize Django project & environment.

Configure PostgreSQL database connection.

Initialize Apps: users, subscriptions, payments, dashboard, core.

Implement Custom User Model (extending AbstractUser).

Configure SimpleJWT for authentication.

[STOP] Wait for user confirmation after Phase 1.

Phase 2: Subscription Data Architecture
Create Plan and Subscription models.

Implement logic for trial periods and status tracking.

Register models in Django Admin.

Generate and run migrations.

[STOP] Wait for user confirmation after Phase 2.

Phase 3: Stripe Payments Integration
Integrate Stripe SDK.

Build a StripeService wrapper class for business logic.

Implement Checkout Session creation endpoints.

Develop Webhook handler for invoice.paid and customer.subscription.deleted.

[STOP] Wait for user confirmation after Phase 3.

Phase 4: Middleware & Permissions
Create a SubscriptionValidator utility.

Build a custom DRF IsSubscribed permission class.

Apply permissions to a sample "Premium" API endpoint.

[STOP] Wait for user confirmation after Phase 4.

Phase 5: Containerization & Deployment
Configure Dockerfile (Multi-stage build).

Create docker-compose.yml (App, DB, Redis/Celery if needed).

Configure Gunicorn for production serving.

Create a .env.example template.

[STOP] Wait for user confirmation after Phase 5.

Mandatory Rules & Standards
1. Workflow Rules
Incremental Progress: Only generate code for the current phase. Never skip ahead or regenerate the entire project unless explicitly requested.

Modular Design: Keep logic out of views.py where possible; use services.py or selectors.py.

State Management: Do not overwrite existing files without acknowledging the change.

2. Code Quality & Formatting
File Paths: Always state the file path in bold (e.g., **apps/users/models.py**) before the code block.

Python Standards: * Strict adherence to PEP8.

Mandatory use of Type Hints for all function signatures.

Docstrings for complex logic.

Security: Never hardcode secrets. Always use env() or os.getenv().

3. Response Style
Conciseness: Keep explanations brief and focused on the why, not just the what.

Clarity: Use Markdown callouts (> [!NOTE]) for critical implementation details.