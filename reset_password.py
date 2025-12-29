#!/usr/bin/env python
import os
import sys
import django
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

# Reset password for algety user
try:
    user = User.objects.get(username='algety')
    user.set_password('admin123')  # Change this to your desired password
    user.save()
    print(f"Password successfully reset for user: {user.username}")
    print("New password: admin123")
    print("Please change this password after logging in!")
except User.DoesNotExist:
    print("User 'algety' not found")