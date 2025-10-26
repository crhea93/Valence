# Valence

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Django 3.2](https://img.shields.io/badge/django-3.2-green.svg)](https://www.djangoproject.com/)

A web application for creating and analyzing Cognitive Affective Maps (CAMs) in research contexts.

## What is Valence?
Valence is a web app designed to allow researchers to build mind maps (or have subjects build mind maps) on a topic -- these mind maps are known
as cognitive affective maps (CAMs). More information on CAMs and their many uses can
be found on the main Valence website: [https://valence.cascadeinstitute.org/](https://valence.cascadeinstitute.org/).

## Features

- **Interactive CAM Builder**: Create cognitive affective maps with an intuitive drag-and-drop interface
- **Multi-Language Support**: Available in English and German
- **Project Management**: Organize research projects with multiple participants
- **User Roles**: Support for researchers, participants, and administrators
- **CAM Operations**:
  - Create, edit, clone, and delete CAMs
  - Import and export CAMs (JSON format)
  - Generate PDF and image exports
  - Undo/redo functionality
- **Collaboration**: Share projects via links and manage participant access
- **Data Export**: Download individual CAMs or entire project datasets
- **Cloud Storage**: AWS S3 integration for media and exports
- **API Access**: RESTful endpoints for programmatic access

## Technology Stack

- **Backend**: Django 3.2.3 (Python web framework)
- **Database**: PostgreSQL (production), SQLite (development)
- **Frontend**: HTML, CSS, JavaScript
- **Storage**: AWS S3 for media files
- **Deployment**: Heroku-ready with Gunicorn WSGI server
- **Key Libraries**:
  - django-cors-headers (API access)
  - WeasyPrint (PDF generation)
  - boto3 (AWS integration)
  - pandas/numpy (data processing)
  - pytest (testing)


## What is this repository for?
The purpose of this repository is to allow any researcher to create their own server.
If you simply wish to use Valence (instead of develop it or run your own server), please
follow the instructions on our [main Valence website](https://valence.cascadeinstitute.org/)
or simply make an account on the official server: https://cognitiveaffectivemaps.herokuapp.com/users/loginpage?next=/


## Setting Up a Local Development Server

This guide will help you set up Valence on your local machine for development or testing purposes.

### Prerequisites

- Python 3.7 or higher
- PostgreSQL (optional, for production-like development)
- Git

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/crhea93/Valence.git
cd Valence
```

#### 2. Set Up Python Environment

Create and activate a virtual environment (recommended):

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# OR using conda
conda env create -f environment.yml
conda activate valence
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### Database Configuration

Valence supports two database configurations for local development:

#### Option A: SQLite (Recommended for Quick Setup)

SQLite requires no additional database setup and is perfect for local testing.

1. Set the environment variable:
```bash
export DJANGO_LOCAL=True  # On Windows: set DJANGO_LOCAL=True
```

2. Run migrations:
```bash
python manage.py migrate
```

#### Option B: PostgreSQL (Production-Like Environment)

For a setup closer to production, use PostgreSQL.

1. Install PostgreSQL on your system
   - Ubuntu/Debian: `sudo apt-get install postgresql postgresql-contrib`
   - macOS: `brew install postgresql`
   - Windows: Download from [postgresql.org](https://www.postgresql.org/download/)

2. Create a database:
```bash
# Start PostgreSQL service if not running
sudo service postgresql start  # Linux
brew services start postgresql # macOS

# Create database
createdb camdev

# Or using psql:
psql -U postgres
CREATE DATABASE camdev;
\q
```

3. Set the environment variable:
```bash
export DJANGO_DEVELOPMENT=True  # On Windows: set DJANGO_DEVELOPMENT=True
```

4. Update credentials in `cognitiveAffectiveMaps/settings_dev.py` if needed:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'camdev',
        'USER': 'your_postgres_user',
        'PASSWORD': 'your_postgres_password',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```

5. Run migrations:
```bash
python manage.py migrate
```

### Environment Variables

For production deployment or custom configurations, create a `.env-local` file in the project root with the following variables:

```env
# Required for production
SECRET_KEY=your-secret-key-here
DEBUG=True  # Set to False for production

# Database (if using custom PostgreSQL setup)
DBNAME=your_database_name
DBUSER=your_database_user
DBPASSWORD=your_database_password
DBHOST=localhost
DBPORT=5432

# Email Configuration (optional for development)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_PORT=587

# AWS S3 Storage (optional for development)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
```

**Note:** For local development with SQLite or PostgreSQL development mode, you only need to set the `DJANGO_LOCAL` or `DJANGO_DEVELOPMENT` environment variable. The other variables are primarily for production deployments.

### Initial Setup

#### Create a Superuser Account

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account for accessing the Django admin panel.

#### Collect Static Files (Optional for Development)

```bash
python manage.py collectstatic
```

### Running the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at:
- Main application: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/

### Database Structure

The application uses the following main models:
- **Users** (`users/models.py`): Custom user model with project and participant management
- **Blocks** (`block/models.py`): CAM nodes/concepts
- **Links** (`link/models.py`): Relationships between blocks
- **Config Admin** (`config_admin/models.py`): Administrative configuration settings

### Troubleshooting

**Issue: Database connection errors**
- Ensure PostgreSQL is running: `sudo service postgresql status`
- Verify database exists: `psql -l`
- Check credentials in settings file

**Issue: Migration errors**
- Try: `python manage.py migrate --run-syncdb`
- Or reset database (WARNING: deletes all data):
  ```bash
  python manage.py flush
  python manage.py migrate
  ```

**Issue: Static files not loading**
- Run: `python manage.py collectstatic`
- Ensure `DEBUG=True` in development

**Issue: Import errors or missing modules**
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.7+)

### Project Structure

```
Valence/
├── cognitiveAffectiveMaps/     # Main Django project settings
│   ├── settings.py              # Production settings
│   ├── settings_dev.py          # Development settings (PostgreSQL)
│   ├── settings_local.py        # Local settings (SQLite)
│   ├── urls.py                  # URL routing
│   └── wsgi.py                  # WSGI application
├── users/                       # User management app
├── block/                       # CAM blocks/nodes app
├── link/                        # CAM links/relationships app
├── config_admin/                # Admin configuration app
├── static/                      # Static files (CSS, JS, images)
├── templates/                   # HTML templates
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── Procfile                     # Heroku deployment config
```

### Next Steps

- Access the admin panel to configure projects and settings
- Create test users and projects
- Explore the API endpoints at `/block/`, `/link/`, `/users/`
- Read the full documentation at https://crhea93.github.io/Valence/

### Running Tests

Valence includes comprehensive unit tests with **126+ tests** covering backend functionality. To run the test suite:

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test users
python manage.py test block
python manage.py test link

# Run with pytest (alternative)
pytest

# Run with verbose output
python manage.py test --verbosity=2

# Run with coverage report
coverage run --source='.' manage.py test
coverage report
```

#### Test Suite Overview

The test suite includes:
- **User Operations (34 tests)**: Authentication, CAM operations, project management
- **Block Operations (11 tests)**: CRUD, drag/drop, resize, validation
- **Link Operations (13 tests)**: CRUD, direction swap, cascade deletion
- **Import/Export (10 tests)**: ZIP file handling, CSV validation
- **Email Functionality (13 tests)**: Contact forms, CAM sharing, password reset
- **API Endpoints (20 tests)**: JSON responses, error handling, validation
- **Permissions (25 tests)**: Access control, authentication, authorization

Test files are located in:
- `users/tests.py` - User authentication and CAM management
- `users/test_import_export.py` - Import/export functionality
- `users/test_email.py` - Email sending and validation
- `users/test_api.py` - API endpoint testing
- `users/test_permissions.py` - Permission and access control
- `block/tests.py` - CAM block/node operations
- `link/tests.py` - CAM link/relationship operations

**For detailed testing documentation, see [TESTING.md](TESTING.md)**

## API Documentation

Valence provides RESTful API endpoints for programmatic access to CAM data.

### Authentication Endpoints

- `POST /users/signup` - Create new user account
- `POST /users/loginpage` - User login
- `GET /users/logout` - User logout
- `POST /users/password_reset/` - Request password reset

### CAM Management Endpoints

- `POST /users/create_individual_cam` - Create a new CAM
- `GET /users/load_cam` - Load existing CAM data
- `POST /users/delete_cam` - Delete a CAM
- `GET /users/download_cam` - Download CAM as JSON
- `POST /users/clone_cam` - Clone an existing CAM
- `POST /users/update_cam_name` - Update CAM name
- `POST /users/export_CAM` - Export CAM as PDF/image
- `POST /users/import_CAM` - Import CAM from JSON

### Block (Node) Endpoints

- `POST /block/add_block` - Add a new block/node to CAM
- `POST /block/update_block` - Update block properties
- `POST /block/delete_block` - Delete a block
- `POST /block/drag_function` - Update block position
- `POST /block/resize_block` - Resize a block
- `POST /block/update_text_size` - Update text size

### Link (Edge) Endpoints

- `POST /link/add_link` - Create connection between blocks
- `POST /link/update_link` - Update link properties
- `POST /link/delete_link` - Delete a link
- `POST /link/update_link_pos` - Update link position
- `POST /link/swap_link_direction` - Reverse link direction

### Project Management Endpoints

- `POST /users/create_project` - Create new research project
- `GET /users/project_page` - View project details
- `POST /users/join_project` - Join project with code
- `GET /users/join_project_link` - Join via direct link
- `POST /users/delete_project` - Delete a project
- `GET /users/download_project` - Download all project data
- `POST /users/project_settings` - Update project settings

**Note**: Most endpoints require authentication. API responses are in JSON format. For detailed request/response schemas, refer to the full documentation at https://crhea93.github.io/Valence/.

## Security Considerations

When deploying Valence to production, ensure you follow these security best practices:

### Required Security Settings

1. **SECRET_KEY**: Generate a strong, random secret key
   ```bash
   # Generate a secure secret key
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```
   Store this in your environment variables, never in code.

2. **DEBUG Mode**: Always set `DEBUG=False` in production
   ```env
   DEBUG=False
   ```

3. **ALLOWED_HOSTS**: Specify your domain explicitly
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Database Credentials**: Use strong passwords and restrict database access
   - Never commit database credentials to version control
   - Use environment variables for all sensitive data
   - Restrict PostgreSQL access to specific IP addresses

5. **HTTPS**: Always use HTTPS in production
   - Configure SSL certificates (Let's Encrypt recommended)
   - Set `SECURE_SSL_REDIRECT = True` in settings
   - Enable `SESSION_COOKIE_SECURE = True` and `CSRF_COOKIE_SECURE = True`

6. **AWS S3 Security**:
   - Use IAM roles with minimal required permissions
   - Enable bucket encryption
   - Set appropriate CORS policies
   - Never expose AWS credentials in client-side code

### Additional Recommendations

- Regularly update dependencies: `pip list --outdated`
- Enable Django's security middleware (already configured)
- Set up database backups with encryption
- Implement rate limiting for API endpoints
- Monitor logs for suspicious activity
- Use strong password requirements for user accounts
- Enable two-factor authentication for admin accounts (if available)

## Production Deployment

### Deploying to Heroku

Valence is configured for Heroku deployment out of the box.

1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

2. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL Database**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY='your-generated-secret-key'
   heroku config:set DEBUG=False
   heroku config:set DJANGO_SETTINGS_MODULE=cognitiveAffectiveMaps.settings
   
   # Email settings (optional)
   heroku config:set EMAIL_HOST='smtp.gmail.com'
   heroku config:set EMAIL_HOST_USER='your-email@example.com'
   heroku config:set EMAIL_HOST_PASSWORD='your-email-password'
   heroku config:set EMAIL_PORT=587
   
   # AWS S3 settings (recommended for production)
   heroku config:set AWS_ACCESS_KEY_ID='your-aws-key'
   heroku config:set AWS_SECRET_ACCESS_KEY='your-aws-secret'
   heroku config:set AWS_STORAGE_BUCKET_NAME='your-bucket-name'
   ```

5. **Deploy**:
   ```bash
   git push heroku master
   ```

6. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   ```

7. **Create Superuser**:
   ```bash
   heroku run python manage.py createsuperuser
   ```

8. **Collect Static Files**:
   ```bash
   heroku run python manage.py collectstatic --noinput
   ```

### Deploying to Other Platforms

For deployment to AWS, DigitalOcean, or other platforms:

1. Set up a Linux server (Ubuntu 20.04+ recommended)
2. Install Python 3.7+, PostgreSQL, Nginx, and Gunicorn
3. Configure Nginx as a reverse proxy to Gunicorn
4. Set up systemd service for automatic startup
5. Configure SSL with Let's Encrypt
6. Set all environment variables in `/etc/environment` or systemd service file

Refer to the Django deployment documentation: https://docs.djangoproject.com/en/3.2/howto/deployment/

## Citation

If you use Valence in your research, please cite:

```bibtex
@software{Rhea2020,
  title={Valence software release},
  author={Rhea, Carter and Thibeault, Christian and Reuter, Lisa 
          and Piereder, Jinelle and Mansell, Jordan},
  year={2020}
}
```

Additional information on CAMs and research applications can be found at:
- Google Scholar: https://scholar.google.ca/citations?view_op=view_citation&hl=en&user=zzpsCKsAAAAJ&citation_for_view=zzpsCKsAAAAJ:5nxA0vEk-isC
- OSF Repository: https://osf.io/9tza2/
- Main Website: https://valence.cascadeinstitute.org/

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This means you are free to use, modify, and distribute this software, provided that:
- You disclose the source code
- You license any derivative works under GPL v3.0
- You include the original copyright and license notice

## How can I contribute?
If you wish to contribute, please check out the current issues (or make a new one!), or simply email us at thibeaultrheaprogramming@gmail.com to get involved.
We have documentation set up at https://crhea93.github.io/Valence/.

Further information on this tool can be found at https://osf.io/9tza2/.


## Authors:
This code was funded by the University of Waterloo's Basille School and the LivMats
Cluster at the University of Freiburg. The code was programmed solely by Carter Rhea
and Christian Thibeault. The primary Valence website was constructed by
[Vibrant Content](https://vibrantcontent.ca/). 
