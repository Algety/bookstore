# Migration to create sample book data

from django.db import migrations


def create_sample_data(apps, schema_editor):
    """Create sample book data if it doesn't already exist"""
    Category = apps.get_model('books', 'Category')
    Book = apps.get_model('books', 'Book')
    BookContributor = apps.get_model('books', 'BookContributor')
    Publisher = apps.get_model('books', 'Publisher')
    
    # First, clean up any records with empty slugs that might cause conflicts
    BookContributor.objects.filter(slug='').delete()
    Publisher.objects.filter(slug='').delete()
    Category.objects.filter(slug='').delete()
    Book.objects.filter(slug='').delete()
    
    # Only create data if the database is empty (preserve existing data)
    if Book.objects.exists() or Category.objects.exists():
        print("Data already exists. Skipping sample data creation to "
              "preserve existing data.")
        return
    
    # Create categories (use get_or_create to avoid conflicts)
    fiction_cat, created = Category.objects.get_or_create(
        slug="fiction",
        defaults={
            "name": "Fiction",
            "screen_name": "Fiction",
            "subcategory": "fiction",
            "age_groups": ["children"],
            "order": 1,
            "active": True
        }
    )
    
    # Create publisher
    publisher, created = Publisher.objects.get_or_create(
        slug="a-ba-ba-ha-la-ma-ha",
        defaults={
            "name": "A-BA-BA-HA-LA-MA-HA"
        }
    )
    
    # Create authors
    author1, created = BookContributor.objects.get_or_create(
        slug="hans-christian-andersen",
        defaults={
            "name": "Hans Christian Andersen",
            "role": "author"
        }
    )
    
    illustrator1, created = BookContributor.objects.get_or_create(
        slug="vladyslav-yerko",
        defaults={
            "name": "Vladyslav Yerko",
            "role": "illustrator"
        }
    )
    
    # Create books
    book1, created = Book.objects.get_or_create(
        slug="the-snow-queen",
        defaults={
            "title": "The Snow Queen",
            "cover_type": "hardcover",
            "publisher": publisher,
            "illustration_type": "color",
            "language": "eng",
            "pages": 48,
            "price": 12.99,
            "stock_quantity": 10,
            "available": True,
            "description": "A classic fairy tale by Hans Christian Andersen."
        }
    )
    
    book2, created = Book.objects.get_or_create(
        slug="the-tinderbox",
        defaults={
            "title": "The Tinderbox",
            "cover_type": "hardcover",
            "publisher": publisher,
            "illustration_type": "color",
            "language": "eng",
            "pages": 32,
            "price": 10.99,
            "stock_quantity": 15,
            "available": True,
            "description": ("Another beloved fairy tale by "
                            "Hans Christian Andersen.")
        }
    )
    
    # Add relationships
    book1.categories.add(fiction_cat)
    book1.authors.add(author1)
    book1.illustrators.add(illustrator1)
    
    book2.categories.add(fiction_cat)
    book2.authors.add(author1)
    book2.illustrators.add(illustrator1)


def remove_sample_data(apps, schema_editor):
    """Remove only the sample data we created, not all data"""
    Book = apps.get_model('books', 'Book')
    Category = apps.get_model('books', 'Category')
    BookContributor = apps.get_model('books', 'BookContributor')
    Publisher = apps.get_model('books', 'Publisher')
    
    # Only remove the specific sample data we created
    Book.objects.filter(slug__in=['the-snow-queen', 'the-tinderbox']).delete()
    Category.objects.filter(slug='fiction').delete()
    BookContributor.objects.filter(
        slug__in=['hans-christian-andersen', 'vladyslav-yerko']
    ).delete()
    Publisher.objects.filter(slug='a-ba-ba-ha-la-ma-ha').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0011_load_initial_data'),
    ]

    operations = [
        migrations.RunPython(create_sample_data, remove_sample_data),
    ]
