#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Book, Category, Publisher, BookContributor


def import_books():
    """Import books from JSON file to Heroku database"""
    with open('local_books_export.json', 'r', encoding='utf-8') as f:
        books_data = json.load(f)
    
    imported_count = 0
    
    for book_data in books_data:
        print(f"Importing: {book_data['title']}")
        
        # Get or create publisher
        publisher = None
        if book_data['publisher']:
            publisher, created = Publisher.objects.get_or_create(
                name=book_data['publisher'],
                defaults={'name': book_data['publisher']}
            )
        
        # Create the book (use get_or_create to avoid duplicates)
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            defaults={
                'price': book_data['price'],
                'publisher': publisher,
                'description': book_data['description'],
                'pages': book_data['pages'],
                'language': book_data['language'],
                'cover_type': book_data['cover_type'],
                'stock_quantity': book_data['stock_quantity'],
                'available': book_data['available']
            }
        )
        
        if created:
            imported_count += 1
            print(f"  ✓ Created new book: {book.title}")
        else:
            print(f"  - Book already exists: {book.title}")
        
        # Add authors
        for author_name in book_data['authors']:
            if author_name:  # Skip empty names
                author, created = BookContributor.objects.get_or_create(
                    name=author_name,
                    defaults={'name': author_name, 'role': 'author'}
                )
                book.authors.add(author)
        
        # Add illustrators  
        for illustrator_name in book_data['illustrators']:
            if illustrator_name:  # Skip empty names
                illustrator, created = BookContributor.objects.get_or_create(
                    name=illustrator_name,
                    defaults={'name': illustrator_name, 'role': 'illustrator'}
                )
                book.illustrators.add(illustrator)
        
        # Add to existing Fairy Tales category
        try:
            fairy_tales = Category.objects.get(name='Fairy Tales')
            book.categories.add(fairy_tales)
            print(f"  ✓ Added to Fairy Tales category")
        except Category.DoesNotExist:
            print(f"  ! Fairy Tales category not found")
    
    print(f"\\nImport complete! Imported {imported_count} new books.")


if __name__ == '__main__':
    import_books()