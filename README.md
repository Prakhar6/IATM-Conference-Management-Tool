# IATM Conference Management Tool

A full-featured academic conference management platform built with Django. Handles the complete conference lifecycle — from registration and payments to paper submissions, peer review, scheduling, and virtual event support.

## Features

### User & Membership
- Email-based authentication (no username required)
- Role-based access: **Author**, **Reviewer**, **Chair**
- Editable profiles with organization, country, and occupation fields
- IATM membership tracking with member-exclusive discounts

### Registration & Payments
- Tiered registration pricing (Student, Professional, Sponsor, etc.)
- Early bird and IATM member discounts
- PayPal Checkout SDK integration
- PDF invoice generation (ReportLab)
- QR code tickets and printable name badges
- Group registration (bulk register by email)

### Academic Paper Management
- Paper submission with PDF upload and up to 3 co-authors
- Multi-track support per conference
- Configurable submission deadlines
- Status workflow: Pending → Accepted / Rejected / Revision
- Digital proceedings — searchable archive of accepted papers

### Peer Review System
- Chair-managed reviewer assignments
- Blind review mode (hides author identity from reviewers)
- Review recommendations: Accept, Reject, Revise
- Automatic submission status updates based on reviews
- Author view of received reviews

### Schedule & Virtual Events
- Session scheduling with multiple types: Keynote, Paper, Workshop, Panel, Break, Social
- Speaker directory with bios and linked sessions
- Timezone toggle (event time vs. local time)
- Zoom integration with meeting URL, ID, and passcode fields
- Gatekept session access (paid registrants only)
- Attendance tracking for certificate eligibility

### Email Communication
- Automated emails: submission confirmation, reviewer assignment, review notification, registration confirmation
- Bulk email with audience segmentation (all, paid, unpaid, authors, reviewers)
- Quick email templates (Call for Papers, Reminder, Thank You)
- Configurable SMTP (defaults to console backend for dev)

### Admin Command Center
- Conference analytics dashboard (registrations, revenue, roles, geography, occupations)
- CSV export for attendee lists and financial reports
- Admin conference dashboard with role management
- Registration tier management via Django admin

### Internationalization
- Multi-language support: English, Spanish, French, Chinese (Simplified), Arabic
- Language switcher in sidebar
- Django i18n with `i18n_patterns` URL routing

### Mobile Responsive
- Collapsible sidebar with mobile hamburger menu
- Responsive grid layouts across all templates
- Touch-friendly cards and forms

## Tech Stack

| Layer       | Technology                                    |
|-------------|-----------------------------------------------|
| Backend     | Django 5.2, Python 3.11                       |
| Database    | PostgreSQL 16                                 |
| Frontend    | Bootstrap 5, Font Awesome, Google Fonts (Inter) |
| Forms       | django-crispy-forms + crispy-bootstrap5       |
| Payments    | PayPal Checkout SDK                           |
| PDF         | ReportLab                                     |
| QR Codes    | qrcode + Pillow                               |
| Deployment  | Docker, Gunicorn, Nginx                       |

## Project Structure

```
cmt project/
├── accounts/          # Custom email-based user auth
├── conference/        # Conference, Track, Payment, RegistrationTier models
├── membership/        # User-conference roles, badges, analytics, bulk email
├── submissions/       # Paper submissions, proceedings, email notifications
├── review/            # Peer review system (assignments, recommendations)
├── schedule/          # Sessions, speakers, attendance, Zoom integration
├── cmt/               # Django settings, root URL config
├── templates/         # Base templates (dashboard.html, base.html)
├── static/            # CSS stylesheets
├── locale/            # Translation files
└── manage.py
```

## Getting Started

### Prerequisites
- Docker & Docker Compose

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ankushrastogi04/IATM-Conference-Management-Tool.git
   cd IATM-Conference-Management-Tool
   ```

2. **Configure environment variables**
   ```bash
   cp "cmt project/.env.example" "cmt project/.env"
   # Edit .env with your settings
   ```

3. **Start with Docker Compose**
   ```bash
   docker compose up --build -d
   ```

4. **Run migrations**
   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. **Open in browser**
   - App: http://localhost:8000
   - Admin: http://localhost:8000/admin

### Environment Variables

| Variable              | Description                          | Default                        |
|-----------------------|--------------------------------------|--------------------------------|
| `SECRET_KEY`          | Django secret key                    | (insecure default for dev)     |
| `DEBUG`               | Debug mode                           | `True`                         |
| `ALLOWED_HOSTS`       | Comma-separated hostnames            | `localhost,127.0.0.1`          |
| `DB_NAME`             | PostgreSQL database name             | `iatm_conference_db`           |
| `DB_USER`             | PostgreSQL username                  | `iatm_user`                    |
| `DB_PASSWORD`         | PostgreSQL password                  | —                              |
| `DB_HOST`             | Database host                        | `localhost`                    |
| `DB_PORT`             | Database port                        | `5432`                         |
| `PAYPAL_CLIENT_ID`    | PayPal API client ID                 | —                              |
| `PAYPAL_CLIENT_SECRET`| PayPal API client secret             | —                              |
| `PAYPAL_MODE`         | `sandbox` or `live`                  | `sandbox`                      |
| `EMAIL_BACKEND`       | Django email backend                 | `console.EmailBackend`         |
| `EMAIL_HOST`          | SMTP host                            | `smtp.gmail.com`               |
| `EMAIL_PORT`          | SMTP port                            | `587`                          |
| `EMAIL_HOST_USER`     | SMTP username                        | —                              |
| `EMAIL_HOST_PASSWORD` | SMTP password / app password         | —                              |
| `DEFAULT_FROM_EMAIL`  | From address for outgoing emails     | `IATM Conference <noreply@iatm.us>` |

## Data Model

```
CustomUser (email auth)
  ├── Membership (role1, role2, is_paid) ──→ Conference
  │     └── Submissions (paper_title, file, status)
  │           └── Review (recommendation, comment)
  ├── Payment (amount, paypal_order_id, status) ──→ Conference + RegistrationTier
  └── Attendance (joined_at) ──→ Session

Conference
  ├── Track
  ├── RegistrationTier (price, early_bird_price)
  └── Session (speakers M2M, zoom fields, type)
        └── Speaker (name, bio, organization)
```

## Production Deployment

For production, use the provided configs in `cmt project/deploy/`:
- `docker-compose.prod.yml` — App + Nginx reverse proxy
- `gunicorn_config.py` — Gunicorn settings
- `nginx.conf` — Nginx configuration

Key production steps:
1. Set `DEBUG=False` and a strong `SECRET_KEY`
2. Configure a real SMTP email backend
3. Set up PayPal live credentials
4. Use HTTPS with SSL certificates
5. Run `python manage.py collectstatic`

## License

This project is developed for the International Association of Technology Management (IATM).
