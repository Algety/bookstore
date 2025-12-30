from django.core.management.base import BaseCommand
from books.models import Category


class Command(BaseCommand):
    help = 'Restore original bookstore categories from September/October 2024'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Starting category restoration...")
        
        current_count = Category.objects.count()
        self.stdout.write(f"Current categories count: {current_count}")
        
        if current_count > 0:
            self.stdout.write("🗑️  Clearing existing categories...")
            Category.objects.all().delete()
        
        # Original category structure
        categories_structure = [
            # Parent categories
            {"name": "children", "screen_name": "Children", "subcategory": None, "age_groups": ["children"], "parent_name": None, "order": 1, "active": True},
            {"name": "teens", "screen_name": "Teens and Youth", "subcategory": None, "age_groups": ["teens"], "parent_name": None, "order": 2, "active": True},
            {"name": "adults", "screen_name": "Adults", "subcategory": None, "age_groups": ["adults"], "parent_name": None, "order": 3, "active": True},
            {"name": "learn_english", "screen_name": "Studying English", "subcategory": None, "age_groups": ["children", "teens", "adults"], "parent_name": None, "order": 4, "active": True},
            {"name": "specials", "screen_name": "Collectible and Gift Editions", "subcategory": None, "age_groups": ["children", "teens", "adults"], "parent_name": None, "order": 5, "active": True},
            
            # Children subcategories
            {"name": "fiction", "screen_name": "Fiction and Fairy tales", "subcategory": "fiction", "age_groups": ["children"], "parent_name": "children", "order": 1, "active": True},
            {"name": "nfiction", "screen_name": "Non-fiction", "subcategory": "nonfiction", "age_groups": ["children"], "parent_name": "children", "order": 2, "active": True},
            {"name": "learning", "screen_name": "Early Learning", "subcategory": "learning", "age_groups": ["children"], "parent_name": "children", "order": 3, "active": True},
            {"name": "crafts", "screen_name": "Craft and Activities", "subcategory": "hobby", "age_groups": ["children"], "parent_name": "children", "order": 4, "active": True},
            
            # Teens subcategories
            {"name": "fiction", "screen_name": "Fiction", "subcategory": "fiction", "age_groups": ["teens"], "parent_name": "teens", "order": 1, "active": True},
            {"name": "nfiction", "screen_name": "Non-fiction", "subcategory": "nonfiction", "age_groups": ["teens"], "parent_name": "teens", "order": 2, "active": True},
            {"name": "learning", "screen_name": "Study and school", "subcategory": "learning", "age_groups": ["teens"], "parent_name": "teens", "order": 3, "active": True},
            {"name": "hobby", "screen_name": "Hobby", "subcategory": "hobby", "age_groups": ["teens"], "parent_name": "teens", "order": 4, "active": True},
            
            # Adults subcategories
            {"name": "fiction", "screen_name": "Fiction", "subcategory": "fiction", "age_groups": ["adults"], "parent_name": "adults", "order": 1, "active": True},
            {"name": "nfiction", "screen_name": "Non-fiction", "subcategory": "nonfiction", "age_groups": ["adults"], "parent_name": "adults", "order": 2, "active": True},
            {"name": "hobby", "screen_name": "Hobby", "subcategory": "hobby", "age_groups": ["adults"], "parent_name": "adults", "order": 3, "active": True},
            
            # English learning levels
            {"name": "alevel", "screen_name": "A1 - A2", "subcategory": "learning", "age_groups": ["children", "teens", "adults"], "parent_name": "learn_english", "order": 1, "active": True},
            {"name": "blevel", "screen_name": "B1 - B2", "subcategory": "learning", "age_groups": ["children", "teens", "adults"], "parent_name": "learn_english", "order": 2, "active": True},
            {"name": "clevel", "screen_name": "C1 - C2", "subcategory": "learning", "age_groups": ["children", "teens", "adults"], "parent_name": "learn_english", "order": 3, "active": True},
            
            # Specials subcategory
            {"name": "specials", "screen_name": "Collectible and Gift Editions", "subcategory": "specials", "age_groups": ["children", "teens", "adults"], "parent_name": "specials", "order": 1, "active": True}
        ]
        
        # Create parent categories first
        self.stdout.write("🏗️  Creating parent categories...")
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
                    self.stdout.write(f"   ✅ Created: {category.screen_name}")
        
        # Create child categories
        self.stdout.write("🌿 Creating child categories...")
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
                        self.stdout.write(f"   ✅ Created: {category.screen_name} → {parent.screen_name}")
                except Category.DoesNotExist:
                    self.stdout.write(f"   ❌ Parent not found: {cat_data['parent_name']}")
        
        final_count = Category.objects.count()
        self.stdout.write(f"\n✅ Restoration complete! Total categories: {final_count}")
        
        # Show structure
        self.stdout.write("\n📋 Restored Category Structure:")
        for parent in Category.objects.filter(parent=None).order_by('order'):
            self.stdout.write(f"\n{parent.order}. {parent.screen_name}")
            for child in parent.subcategories.all().order_by('order'):
                self.stdout.write(f"   • {child.screen_name}")
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Category restoration completed successfully!'))