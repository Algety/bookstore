#!/usr/bin/env python
"""
Safe script to restore original bookstore categories.
This script can be run on both local and Heroku environments.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Category


def restore_original_categories():
    """
    Restore the original category structure from September/October 2024.
    This will clear existing categories and restore the original 5-category structure.
    """
    
    print("🔄 Starting category restoration...")
    print(f"Current categories count: {Category.objects.count()}")
    
    # Confirm before proceeding
    if Category.objects.exists():
        print("\n⚠️  This will DELETE all existing categories and restore the original structure.")
        confirmation = input("Are you sure you want to proceed? (type 'yes' to continue): ")
        if confirmation.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
    
    # Clear existing categories
    print("\n🗑️  Clearing existing categories...")
    Category.objects.all().delete()
    
    # Original category structure from September/October 2024
    categories_structure = [
        # Main parent categories (age-based organization)
        {
            "name": "children",
            "screen_name": "Children",
            "subcategory": None,
            "age_groups": ["children"],
            "parent_name": None,
            "order": 1,
            "active": True
        },
        {
            "name": "teens", 
            "screen_name": "Teens and Youth",
            "subcategory": None,
            "age_groups": ["teens"],
            "parent_name": None,
            "order": 2,
            "active": True
        },
        {
            "name": "adults",
            "screen_name": "Adults", 
            "subcategory": None,
            "age_groups": ["adults"],
            "parent_name": None,
            "order": 3,
            "active": True
        },
        {
            "name": "learn_english",
            "screen_name": "Studying English",
            "subcategory": None,
            "age_groups": ["children", "teens", "adults"],
            "parent_name": None,
            "order": 4,
            "active": True
        },
        {
            "name": "specials",
            "screen_name": "Collectible and Gift Editions",
            "subcategory": None, 
            "age_groups": ["children", "teens", "adults"],
            "parent_name": None,
            "order": 5,
            "active": True
        },
        
        # Children's subcategories
        {
            "name": "fiction",
            "screen_name": "Fiction and Fairy tales",
            "subcategory": "fiction",
            "age_groups": ["children"],
            "parent_name": "children",
            "order": 1,
            "active": True
        },
        {
            "name": "nfiction",
            "screen_name": "Non-fiction", 
            "subcategory": "nonfiction",
            "age_groups": ["children"],
            "parent_name": "children",
            "order": 2,
            "active": True
        },
        {
            "name": "learning",
            "screen_name": "Early Learning",
            "subcategory": "learning",
            "age_groups": ["children"],
            "parent_name": "children",
            "order": 3,
            "active": True
        },
        {
            "name": "crafts",
            "screen_name": "Craft and Activities",
            "subcategory": "hobby",
            "age_groups": ["children"],
            "parent_name": "children", 
            "order": 4,
            "active": True
        },
        
        # Teens' subcategories
        {
            "name": "fiction",
            "screen_name": "Fiction",
            "subcategory": "fiction",
            "age_groups": ["teens"],
            "parent_name": "teens",
            "order": 1,
            "active": True
        },
        {
            "name": "nfiction", 
            "screen_name": "Non-fiction",
            "subcategory": "nonfiction",
            "age_groups": ["teens"],
            "parent_name": "teens",
            "order": 2,
            "active": True
        },
        {
            "name": "learning",
            "screen_name": "Study and school",
            "subcategory": "learning",
            "age_groups": ["teens"],
            "parent_name": "teens",
            "order": 3,
            "active": True
        },
        {
            "name": "hobby",
            "screen_name": "Hobby",
            "subcategory": "hobby", 
            "age_groups": ["teens"],
            "parent_name": "teens",
            "order": 4,
            "active": True
        },
        
        # Adults' subcategories
        {
            "name": "fiction",
            "screen_name": "Fiction",
            "subcategory": "fiction",
            "age_groups": ["adults"],
            "parent_name": "adults",
            "order": 1,
            "active": True
        },
        {
            "name": "nfiction",
            "screen_name": "Non-fiction",
            "subcategory": "nonfiction", 
            "age_groups": ["adults"],
            "parent_name": "adults",
            "order": 2,
            "active": True
        },
        {
            "name": "hobby",
            "screen_name": "Hobby",
            "subcategory": "hobby",
            "age_groups": ["adults"],
            "parent_name": "adults",
            "order": 3,
            "active": True
        },
        
        # English learning levels
        {
            "name": "alevel",
            "screen_name": "A1 - A2",
            "subcategory": "learning",
            "age_groups": ["children", "teens", "adults"],
            "parent_name": "learn_english",
            "order": 1,
            "active": True
        },
        {
            "name": "blevel",
            "screen_name": "B1 - B2", 
            "subcategory": "learning",
            "age_groups": ["children", "teens", "adults"],
            "parent_name": "learn_english",
            "order": 2,
            "active": True
        },
        {
            "name": "clevel",
            "screen_name": "C1 - C2",
            "subcategory": "learning",
            "age_groups": ["children", "teens", "adults"],
            "parent_name": "learn_english",
            "order": 3,
            "active": True
        },
        
        # Specials subcategory
        {
            "name": "specials",
            "screen_name": "Collectible and Gift Editions",
            "subcategory": "specials",
            "age_groups": ["children", "teens", "adults"],
            "parent_name": "specials",
            "order": 1,
            "active": True
        }
    ]
    
    # First pass: create parent categories
    print("\n🏗️  Creating parent categories...")
    parent_count = 0
    for cat_data in categories_structure:
        if not cat_data['parent_name']:
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
                print(f"   ✅ Created: {category.screen_name}")
                parent_count += 1
            else:
                print(f"   ⚠️  Already exists: {category.screen_name}")
    
    # Second pass: create child categories  
    print("\n🌿 Creating child categories...")
    child_count = 0
    for cat_data in categories_structure:
        if cat_data['parent_name']:
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
                    print(f"   ✅ Created: {category.screen_name} → {parent.screen_name}")
                    child_count += 1
                else:
                    print(f"   ⚠️  Already exists: {category.screen_name} → {parent.screen_name}")
            except Category.DoesNotExist:
                print(f"   ❌ Parent not found: {cat_data['parent_name']} for {cat_data['name']}")
    
    final_count = Category.objects.count()
    print(f"\n✅ Restoration complete!")
    print(f"📊 Created {parent_count} parent categories and {child_count} child categories")
    print(f"🎯 Total categories: {final_count}")
    
    # Display the restored structure
    print("\n📋 Restored Category Structure:")
    for parent in Category.objects.filter(parent=None).order_by('order'):
        print(f"\n{parent.order}. {parent.screen_name}")
        for child in parent.subcategories.all().order_by('order'):
            print(f"   • {child.screen_name}")


if __name__ == '__main__':
    restore_original_categories()