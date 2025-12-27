#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import django
from django.core.files import File
from django.core.files.storage import default_storage

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()

from books.models import Book


def upload_and_assign_images():
    """Upload local images to S3 and assign them to books"""
    
    # Image mappings based on the file names in your media folder
    image_mappings = {
        'The Snow Queen': 'SNIGOVA_ANG.jpg',  # or SNIGOVA_ANG_x9J0R9T.jpg
        'The Tinderbox': 'Tinderbox.jpg',
    }
    
    media_path = os.path.join(os.path.dirname(__file__), 'media')
    
    for book_title, image_filename in image_mappings.items():
        try:
            book = Book.objects.get(title=book_title)
            image_path = os.path.join(media_path, image_filename)
            
            if os.path.exists(image_path):
                print(f"Processing {book_title}...")
                
                # Open the local image file
                with open(image_path, 'rb') as img_file:
                    # Create Django file object
                    django_file = File(img_file)
                    
                    # Save to the book's image field (this will upload to S3)
                    book.image.save(image_filename, django_file, save=True)
                    
                print(f"  ✓ Uploaded {image_filename} to S3 and assigned to {book_title}")
                print(f"  ✓ Image URL: {book.image.url}")
            else:
                print(f"  ! Image file not found: {image_path}")
                
        except Book.DoesNotExist:
            print(f"  ! Book not found: {book_title}")
        except Exception as e:
            print(f"  ! Error processing {book_title}: {e}")
    
    print("\\nImage upload complete!")


if __name__ == '__main__':
    upload_and_assign_images()