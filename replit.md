# GreenMarket Ecuador

## Overview

GreenMarket Ecuador is an e-commerce platform specializing in eco-friendly automotive products. The platform offers a product catalog with a green-themed design, reflecting a commitment to sustainability. Its purpose is to provide a seamless shopping experience for environmentally conscious consumers while offering robust administrative tools for product and site management. The project aims to capture a niche market for sustainable automotive goods, with future ambitions to incorporate AI-driven recommendations and inventory management.

## User Preferences

I prefer concise and direct communication. When making changes, prioritize core functionality and maintain the existing architectural patterns. For new features or significant modifications, please propose the approach before implementation. I value clean, readable code and robust error handling. Ensure all security best practices are followed, especially concerning user data and authentication.

## System Architecture

The application follows a traditional client-server architecture with a Flask backend and a Jinja2-rendered frontend.

**UI/UX Decisions:**
- **Design Theme:** Ecological theme with a primary color palette of #2d7a3e, #4caf50, and #81c784.
- **Responsiveness:** Custom CSS ensures a responsive design across devices.
- **Iconography:** Font Awesome is used for sustainable-themed icons and social media links.
- **Customization:** Administrators can dynamically change the site's primary, secondary, and background colors via a dashboard, with settings stored in the database.

**Technical Implementations:**
- **Backend Framework:** Flask (Python 3.11) handles routing, business logic, and database interactions.
- **Database:** PostgreSQL is used as the relational database, managed via Flask-SQLAlchemy ORM.
- **Image Processing:** Pillow resizes and optimizes product images upon upload, ensuring unique filenames.
- **Authentication:** Werkzeug is used for password hashing (scrypt) and secure session management for both admin and customer users.
- **Frontend Templating:** Jinja2 integrates dynamic content into HTML pages.
- **Shopping Cart & Checkout:** Features a multi-product checkout, dynamic quantity updates, stock validation, and automatic stock reduction post-purchase.
- **User Management:** Includes user registration, login (username/email), profile management, password changes, and order history viewing.
- **Admin Panel:** Provides full CRUD (Create, Read, Update, Delete) functionality for products, site customization, and payment method management.
- **Security:** Implemented server-side input validation, robust error handling, and secure session management using `SESSION_SECRET`.

**Feature Specifications:**
- **Product Catalog:** Grid view, detailed product pages with quantity selectors.
- **Shopping Cart:** Add/remove items, update quantities, calculate totals, stock validation.
- **Checkout:** Multi-product processing, multiple payment options.
- **Admin Dashboard:** Product management, site color customization, payment method toggling, password change for admin.
- **User Accounts:** Registration, login, profile updates, password change, order history.

**System Design Choices:**
- **Database Schema:** Tables for `products`, `admin_users`, `site_config`, `users`, `orders`, and `payment_methods`.
- **Modularity:** Separation of models (`models.py`), main application logic (`main.py`), static assets, and templates.
- **Scalability:** Designed to be compatible with WSGI-compliant hosting services and uses PostgreSQL for data storage.

## External Dependencies

- **PostgreSQL:** Primary relational database, hosted via Neon PostgreSQL on Replit.
- **Flask-SQLAlchemy:** ORM for interacting with PostgreSQL.
- **Pillow:** Python Imaging Library for image processing.
- **Werkzeug:** Utility library for WSGI applications, used for security and file handling.
- **Font Awesome:** Icon library for UI elements.
- **PayPal REST API:** Integrated for processing online payments. Configured via `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, and `PAYPAL_MODE` environment variables.
- **Stripe:** Integrated for secure credit card processing via Stripe Checkout. Configured via `STRIPE_SECRET_KEY` environment variable.
- **Flask-Mail:** Used for sending emails, specifically for the contact form. Configured via SMTP settings (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, etc.)
- **YouTube, Facebook, X (Twitter), WhatsApp:** Social media links integrated into the site header and footer.