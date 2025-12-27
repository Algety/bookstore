# Generated migration for loading initial data

from django.db import migrations
import json
import os


def load_initial_data(apps, schema_editor):
    """Load data from backup.json"""
    # Import models
    Category = apps.get_model('books', 'Category')
    Book = apps.get_model('books', 'Book')
    BookContributor = apps.get_model('books', 'BookContributor')
    Publisher = apps.get_model('books', 'Publisher')
    
    # Get the path to backup.json
    base_dir = os.path.dirname(os.path.dirname(__file__))
    backup_path = os.path.join(base_dir, '..', '..', 'backup.json')
    
    if os.path.exists(backup_path):
        with open(backup_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Load data in order of dependencies
        for item in data:
            model_name = item['model']
            pk = item['pk']
            fields = item['fields']
            
            try:
                if model_name == 'books.category':
                    Category.objects.get_or_create(
                        id=pk,
                        defaults=fields
                    )
                elif model_name == 'books.publisher':
                    Publisher.objects.get_or_create(
                        id=pk,
                        defaults=fields
                    )
                elif model_name == 'books.bookcontributor':
                    BookContributor.objects.get_or_create(
                        id=pk,
                        defaults=fields
                    )
                elif model_name == 'books.book':
                    # Handle many-to-many fields separately
                    categories_data = fields.pop('categories', [])
                    authors_data = fields.pop('authors', [])
                    illustrators_data = fields.pop('illustrators', [])
                    
                    book, created = Book.objects.get_or_create(
                        id=pk,
                        defaults=fields
                    )
                    
                    if created or not book.categories.exists():
                        # Add many-to-many relationships
                        for cat_id in categories_data:
                            try:
                                category = Category.objects.get(id=cat_id)
                                book.categories.add(category)
                            except Category.DoesNotExist:
                                pass
                                
                        for author_id in authors_data:
                            try:
                                author = BookContributor.objects.get(
                                    id=author_id
                                )
                                book.authors.add(author)
                            except BookContributor.DoesNotExist:
                                pass
                                
                        for illustrator_id in illustrators_data:
                            try:
                                illustrator = BookContributor.objects.get(
                                    id=illustrator_id
                                )
                                book.illustrators.add(illustrator)
                            except BookContributor.DoesNotExist:
                                pass
            except Exception as e:
                # Skip items that fail to load
                print(f"Failed to load {model_name} with id {pk}: {e}")
                continue


def reverse_load_initial_data(apps, schema_editor):
    """Remove the loaded data (optional reverse operation)"""
    # You could implement data deletion here if needed
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_book_sku'),
    ]

    operations = [
        migrations.RunPython(load_initial_data, reverse_load_initial_data),
    ]
