# Migration to create sample book data

from django.db import migrations


def create_sample_data(apps, schema_editor):
    """Create sample book data"""
    Category = apps.get_model('books', 'Category')
    Book = apps.get_model('books', 'Book')
    BookContributor = apps.get_model('books', 'BookContributor')
    Publisher = apps.get_model('books', 'Publisher')
    
    # Create categories
    fiction_cat = Category.objects.create(
        name="Fiction",
        screen_name="Fiction",
        subcategory="fiction",
        age_groups=["children"],
        order=1,
        active=True
    )
    
    # Create publisher
    publisher = Publisher.objects.create(
        name="A-BA-BA-HA-LA-MA-HA"
    )
    
    # Create authors
    author1 = BookContributor.objects.create(
        name="Hans Christian Andersen",
        role="author"
    )
    
    illustrator1 = BookContributor.objects.create(
        name="Vladyslav Yerko",
        role="illustrator"
    )
    
    # Create books
    book1 = Book.objects.create(
        title="The Snow Queen",
        cover_type="hardcover",
        publisher=publisher,
        illustration_type="color",
        language="eng",
        pages=48,
        price=12.99,
        stock_quantity=10,
        available=True,
        description="A classic fairy tale by Hans Christian Andersen."
    )
    
    book2 = Book.objects.create(
        title="The Tinderbox",
        cover_type="hardcover",
        publisher=publisher,
        illustration_type="color",
        language="eng",
        pages=32,
        price=10.99,
        stock_quantity=15,
        available=True,
        description="Another beloved fairy tale by Hans Christian Andersen."
    )
    
    # Add relationships
    book1.categories.add(fiction_cat)
    book1.authors.add(author1)
    book1.illustrators.add(illustrator1)
    
    book2.categories.add(fiction_cat)
    book2.authors.add(author1)
    book2.illustrators.add(illustrator1)


def remove_sample_data(apps, schema_editor):
    """Remove sample data"""
    Book = apps.get_model('books', 'Book')
    Category = apps.get_model('books', 'Category')
    BookContributor = apps.get_model('books', 'BookContributor')
    Publisher = apps.get_model('books', 'Publisher')
    
    Book.objects.all().delete()
    Category.objects.all().delete()
    BookContributor.objects.all().delete()
    Publisher.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0011_load_initial_data'),
    ]

    operations = [
        migrations.RunPython(create_sample_data, remove_sample_data),
    ]
