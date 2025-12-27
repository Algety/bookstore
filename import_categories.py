#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Category


def import_categories():
    """Import categories from JSON file to Heroku database"""
    with open('local_categories_export.json', 'r', encoding='utf-8') as f:
        categories_data = json.load(f)
    
    # First pass: create all parent categories
    print("Creating parent categories...")
    for cat_data in categories_data:
        if not cat_data['parent_name']:  # This is a parent category
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                subcategory=cat_data['subcategory'],
                defaults={
                    'screen_name': cat_data['screen_name'],
                    'age_groups': cat_data['age_groups'],
                    'order': cat_data['order'],
                    'active': cat_data['active'],
                    'parent': None
                }
            )
            if created:
                print(f"  ✓ Created parent: {category.name}")
            else:
                print(f"  - Parent exists: {category.name}")
    
    # Second pass: create child categories
    print("\\nCreating child categories...")
    for cat_data in categories_data:
        if cat_data['parent_name']:  # This is a child category
            try:
                parent = Category.objects.get(name=cat_data['parent_name'])
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    parent=parent,
                    subcategory=cat_data['subcategory'],
                    defaults={
                        'screen_name': cat_data['screen_name'],
                        'age_groups': cat_data['age_groups'],
                        'order': cat_data['order'],
                        'active': cat_data['active']
                    }
                )
                if created:
                    print(f"  ✓ Created child: {category.name} (parent: {parent.name})")
                else:
                    print(f"  - Child exists: {category.name} (parent: {parent.name})")
            except Category.DoesNotExist:
                print(f"  ! Parent not found for {cat_data['name']}: {cat_data['parent_name']}")
    
    final_count = Category.objects.count()
    print(f"\\nImport complete! Total categories: {final_count}")


if __name__ == '__main__':
    import_categories()