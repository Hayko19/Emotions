# Emotions — Premium Flower Shop

A full-featured e-commerce platform for a flower shop, built with Django. Includes a product catalog, session-based cart, order checkout, REST API, and a custom sales analytics dashboard.

## Features

- **Product catalog** — filter by category and type (bouquets or single stems); sort by price, name, or newest
- **Product variants** — single-stem products support multiple variants (e.g. different stem lengths or sizes), each with its own price
- **Interactive cart** — add/update/remove items without page reload; tracks product + variant combinations independently
- **Checkout** — order form with automatic delivery fee: free for orders over 5 000 ₽, otherwise +500 ₽
- **Order management** — 5 order statuses (new → processing → delivering → completed / cancelled)
- **Admin dashboard** — revenue stats (today / week / month / all time), order counts by status, top-5 bestsellers, 7-day charts via Chart.js, recent orders list with inline status update
- **REST API** — Django REST Framework with Swagger/OpenAPI docs (drf-yasg)
- **Responsive UI** — smooth animations, glassmorphism navigation, light color palette

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.10+, Django 4.2 |
| REST API | Django REST Framework 3.16, drf-yasg (Swagger) |
| Frontend | Vanilla JS, Modern CSS (Custom Properties), HTML5, Chart.js |
| Database | SQLite (default) |
| Image processing | Pillow |
| Other | django-filter, django-cors-headers, django-admin-sortable2 |

## Getting Started

```bash
# Clone and install dependencies
git clone <your-repo-url>
cd diploma
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# (Optional) seed the database with sample data
python scripts/populate_data.py

# Run the development server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

The custom dashboard is at `/dashboard/` and requires staff or superuser access.

## Project Structure

```
diploma/
├── flowershop/   # Project core (settings, root URLs)
├── shop/         # Main app (models, views, templates, URLs)
├── static/       # CSS, JS, fonts
├── media/        # Uploaded product and banner images
└── scripts/      # Database seed utilities
```

## Data Models

- **Category** — product categories with ordering support
- **Product** — bouquet or single-stem, can be featured on the home page
- **ProductVariant** — optional size/variant with its own price (for single-stem products)
- **Order** + **OrderItem** — customer orders with line items and variant references
