#!/usr/bin/env python
"""Clear categories and load fixture"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/app')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
import django
django.setup()

from books.models import Category

print("Clearing existing categories...")
Category.objects.all().delete()
print("Categories cleared!")

# Now load the fixture
from django.core.management import call_command
print("Loading categories fixture...")
call_command('loaddata', 'categories_backup.json')
print("Categories restored!")

print(f"Total categories now: {Category.objects.count()}")