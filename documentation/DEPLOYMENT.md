# Deployment Guide

This document provides step-by-step instructions for deploying the Fayno Ukrainian Bookstore to Heroku with PostgreSQL database, AWS S3 static file storage, and Stripe payment integration.

## Table of Contents
1. [Create a Database](#create-a-database)
2. [Create Heroku App](#create-heroku-app)
3. [Connect Database to Local Development](#connect-database-to-local-development)
4. [Configure and Deploy Application](#configure-and-deploy-application)
5. [Set Up AWS S3 for Static Files](#set-up-aws-s3-for-static-files)
6. [Configure Stripe Payments](#configure-stripe-payments)
7. [Set Up Email Configuration](#set-up-email-configuration)

## Create a Database

For this project, a Postgres database instance was created on 'PostgreSQL from Code Institute', available to Code Institute students.

## Create Heroku App

1. Log into Heroku
2. Go to the Dashboard and click the "New" button
3. Give the new app a name
4. Select the region closest to you
5. Click the "Create app" button to confirm
6. Open the Settings tab
7. Add the config var `DATABASE_URL`, and for the value add the PostgreSQL database URL obtained when the database was created

## Connect Database to Local Development

### Prepare the project for database connection

**In the terminal:**
1. Install required packages:
   ```bash
   pip3 install dj_database_url==0.5.0 psycopg2
   ```
2. Update requirements file:
   ```bash
   pip freeze > requirements.txt
   ```

**In the settings.py file:**
1. Add `import dj_database_url` below the `import os` line
2. In the DATABASES section, comment out the old SQLite3 configuration
3. Add the new database configuration:
   ```python
   DATABASES = {
       'default': dj_database_url.parse('your-postgresql-database-url')
   }
   ```

### Migrate the database

**In the terminal:**
1. Check migrations: `python3 manage.py showmigrations`
2. Run migrations: `python3 manage.py migrate`
3. Load fixtures (if any): `python3 manage.py loaddata <fixture_name>`
4. Create superuser: `python3 manage.py createsuperuser`

### Secure the database configuration

To prevent exposing the database URL on GitHub:

1. Remove the hardcoded database configuration from settings.py
2. Restore the original SQLite configuration:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       }
   }
   ```

## Configure and Deploy Application

### Create and hide a new SECRET_KEY

1. Generate a new secret key (e.g., using https://randomkeygen.com/)
2. In `env.py` in the root directory, add:
   ```python
   os.environ.setdefault('SECRET_KEY', 'your-new-secret-key')
   ```
3. In `settings.py`, update the SECRET_KEY:
   ```python
   SECRET_KEY = os.environ.get('SECRET_KEY')
   ```

### Configure database settings for both environments

In `settings.py`, replace the DATABASES configuration with:
```python
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else: 
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Update environment import

In `env.py`, update the import to check if the file exists:
```python
if os.path.isfile('env.py'):
    import env
```

### Create deployment files

1. **Create Procfile** in the root directory:
   ```
   web: gunicorn bookstore.wsgi:application
   ```

2. **Create .python-version file** in the root directory:
   ```
   3.11.11
   ```

3. **Update ALLOWED_HOSTS** in settings.py:
   - Add your Heroku app URL (without https:// and trailing slash)

### Install Gunicorn

1. Install Gunicorn: `pip3 install gunicorn`
2. Update requirements: `pip freeze --local > requirements.txt`
3. Commit and push changes to GitHub

### Prepare Heroku for deployment

In Heroku app settings → Config Vars, add:
- `DISABLE_COLLECTSTATIC` = `1` (temporary)
- `SECRET_KEY` = your secret key value

### Deploy the app

1. In Heroku app dashboard → Deploy tab:
   - Select GitHub as deployment method
   - Search for and connect your repository
   - Enable Automatic Deploys
   - Click "Deploy Branch"
2. Click "Open app" to view the deployed application

### Configure DEBUG conditionally

In `settings.py`:
```python
DEBUG = 'DEVELOPMENT' in os.environ
```

In `env.py`:
```python
os.environ.setdefault('DEVELOPMENT', '1')
```

## Set Up AWS S3 for Static Files

### AWS Account Setup

1. Navigate to https://aws.amazon.com
2. Create an AWS account with personal information
3. Complete verification steps
4. Access the AWS Management Console

### Create S3 Bucket

1. Search for S3 service
2. Click "Create bucket"
3. Enter a unique bucket name
4. Select your preferred region
5. Uncheck "Block all public access"
6. Acknowledge public access warning
7. Click "Create bucket"

### Configure Bucket

**Static Website Hosting:**
1. Open bucket → Properties tab
2. Enable Static website hosting
3. Set index.html and error.html as placeholders

**CORS Configuration:**
1. Go to Permissions tab → CORS
2. Add the following configuration:
   ```json
   [
     {
         "AllowedHeaders": ["Authorization"],
         "AllowedMethods": ["GET"],
         "AllowedOrigins": ["*"],
         "ExposeHeaders": []
     }
   ]
   ```

**Bucket Policy:**
1. Permissions tab → Bucket policy
2. Use Policy Generator:
   - Policy Type: S3 Bucket Policy
   - Principal: *
   - Action: GetObject
   - Resource: your-bucket-arn/*
3. Generate and save policy

**Access Control List:**
1. Permissions tab → ACL
2. Enable "List objects" for Everyone

### Create IAM User and Group

**Create Group:**
1. Go to IAM → Groups → Create group
2. Name the group (e.g., "manage-bookstore")

**Create Policy:**
1. IAM → Policies → Create policy
2. Import "AmazonS3FullAccess"
3. Modify Resource to include your bucket ARN:
   ```json
   "Resource": [
       "arn:aws:s3:::your-bucket-name",
       "arn:aws:s3:::your-bucket-name/*"
   ]
   ```
4. Attach policy to group

**Create User:**
1. IAM → Users → Create user
2. Add user to group
3. Generate access credentials
4. Download CSV file with keys

### Connect Django to S3

**Install packages:**
```bash
pip3 install boto3 django-storages
pip3 freeze > requirements.txt
```

**Update settings.py:**
1. Add "storages" to INSTALLED_APPS
2. Add AWS configuration:
   ```python
   if 'USE_AWS' in os.environ:
       AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
       AWS_S3_REGION_NAME = 'us-east-1'
       AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
       AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
       AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
       
       # Cache control
       AWS_S3_OBJECT_PARAMETERS = {
           'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
           'CacheControl': 'max-age=94608000',
       }
       
       # Static and media files
       STATICFILES_STORAGE = 'custom_storages.StaticStorage'
       STATICFILES_LOCATION = 'static'
       DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
       MEDIAFILES_LOCATION = 'media'
       
       # Override static and media URLs in production
       STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/'
       MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/'
   ```

**Create custom_storages.py:**
```python
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION

class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
```

**Update Heroku Config Vars:**
- `AWS_ACCESS_KEY_ID` = your access key
- `AWS_SECRET_ACCESS_KEY` = your secret key
- `USE_AWS` = `True`
- Remove `DISABLE_COLLECTSTATIC`

### Upload Media Files

1. In S3 bucket, create "media" folder
2. Upload product images
3. Grant public read access

## Configure Stripe Payments

### Add Stripe Keys to Heroku

1. Get keys from Stripe dashboard → Developers → API keys
2. Add to Heroku Config Vars:
   - `STRIPE_PUBLIC_KEY`
   - `STRIPE_SECRET_KEY`

### Create Webhook Endpoint

1. Stripe → Webhooks → Add endpoint
2. URL: `https://your-heroku-app.herokuapp.com/checkout/wh/`
3. Select relevant events
4. Copy webhook signing secret
5. Add to Heroku: `STRIPE_WH_SECRET`

## Set Up Email Configuration

### Generate Gmail App Password

1. Enable 2-factor authentication on Gmail
2. Generate app-specific password
3. Copy the 16-character password

### Configure Django Email Settings

**Add to Heroku Config Vars:**
- `EMAIL_HOST_USER` = your Gmail address
- `EMAIL_HOST_PASS` = 16-character app password

**Update settings.py:**
```python
if 'DEVELOPMENT' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'test@example.com'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASS')
    DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER')
```

### Test Email System

1. Register a new user account
2. Check email delivery
3. Verify confirmation links work

## Final Steps

1. Confirm superuser email in Django admin
2. Test all functionality
3. Monitor Heroku logs for any issues

---

**Deployment Complete!** Your Fayno Ukrainian Bookstore should now be fully deployed and functional.