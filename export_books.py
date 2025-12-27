#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Book, Category, Publisher, BookContributor

def export_books():
    """Export books data to JSON file"""
    books_data = []
    
    for book in Book.objects.all():
        book_data = {
            'title': book.title,
            'price': float(book.price) if book.price else 0,
            'authors': [a.name for a in book.authors.all()],
            'illustrators': [i.name for i in book.illustrators.all()],
            'categories': [c.name for c in book.categories.all()],
            'publisher': book.publisher.name if book.publisher else None,
            'description': book.description or '',
            'pages': book.pages or 0,
            'language': book.language or 'eng',
            'cover_type': book.cover_type or 'paperback',
            'stock_quantity': book.stock_quantity or 0,
            'available': book.available if hasattr(book, 'available') else True
        }
        books_data.append(book_data)
    
    # Export to JSON with UTF-8 encoding
    with open('local_books_export.json', 'w', encoding='utf-8') as f:
        json.dump(books_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(books_data)} books to local_books_export.json")
    
    # Print summary
    print("\nExported books:")
    for book in books_data:
        print(f"- {book['title']} by {', '.join(book['authors'])}")

if __name__ == '__main__':
    export_books()