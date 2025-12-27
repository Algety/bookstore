#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Category


def export_categories():
    """Export categories data to JSON file"""
    categories_data = []
    
    for category in Category.objects.all():
        category_data = {
            'name': category.name,
            'screen_name': category.screen_name or category.name,
            'subcategory': category.subcategory,
            'age_groups': category.age_groups or [],
            'parent_name': category.parent.name if category.parent else None,
            'order': category.order,
            'active': category.active
        }
        categories_data.append(category_data)
    
    # Export to JSON with UTF-8 encoding
    with open('local_categories_export.json', 'w', encoding='utf-8') as f:
        json.dump(categories_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(categories_data)} categories to local_categories_export.json")
    
    # Print summary
    print("\nExported categories:")
    for cat in categories_data:
        parent_info = f" (parent: {cat['parent_name']})" if cat['parent_name'] else ""
        print(f"- {cat['name']}{parent_info}")


if __name__ == '__main__':
    export_categories()