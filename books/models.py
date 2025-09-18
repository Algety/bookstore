from django.db import models
from slugify import slugify
from multiselectfield import MultiSelectField

# Create your models here.
class Category(models.Model):

    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('nonfiction', 'Non-fiction'),
        ('learning', 'Learning'),
        ('hobby', 'Hobby'),   
        ('specials', 'Specials'),
    ]

    AGE_GROUP_CHOICES = [
        ('children', 'Children'),
        ('teens', 'Teens'),
        ('adults', 'Adults'),
        ('all', 'All'),
    ]

    name = models.CharField(max_length=100)
    screen_name = models.CharField(max_length=254, null=True, blank=True)
    subcategory = models.CharField(max_length=50, choices=GENRE_CHOICES, null=True, blank=True)
    age_groups = MultiSelectField(choices=AGE_GROUP_CHOICES, blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        limit_choices_to={'subcategory__isnull': True}
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first")
    active = models.BooleanField(default=True, help_text="Uncheck to hide this category from public view")

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name}"
    
    def get_screen_name(self):
        return self.screen_name
    
    def get_age_group_labels(self):
        label_map = dict(self.AGE_GROUP_CHOICES)
        return [label_map.get(code, code) for code in self.age_groups or []]


class BookContributor(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    role = models.CharField(
        max_length=30,
        choices=[
            ('author', 'Author'),
            ('illustrator', 'Illustrator'),
        ]
    )
    about = models.TextField(blank=True)
    photo_url = models.URLField(max_length=1024, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)    

    def __str__(self):
        return self.name


class Book(models.Model):
    categories = models.ManyToManyField(Category, related_name='books')
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True, blank=True)
    authors = models.ManyToManyField(
        BookContributor,
        blank=True,
        related_name='authored_books',
        limit_choices_to={'role': 'author'}
    )

    COVER_CHOICES = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
    ]
    cover_type = models.CharField(max_length=10, choices=COVER_CHOICES)

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )

    ILLUSTRATION_CHOICES = [
        ('none', 'No illustrations'),
        ('bw', 'Black & White'),
        ('color', 'Full Colour'),
    ]
    illustration_type = models.CharField(max_length=10, choices=ILLUSTRATION_CHOICES)

    illustrators = models.ManyToManyField(
        BookContributor,
        blank=True,
        related_name='illustrated_books',
        limit_choices_to={'role': 'illustrator'}
    )

    LANGUAGE_CHOICES = [
        ('eng', 'English'),
        ('ukr', 'Ukrainian'),
    ]
    language = models.CharField(max_length=30, choices=LANGUAGE_CHOICES,
                                default='ukr')

    pages = models.PositiveIntegerField()
    dimensions = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, 
                                 blank=True)

    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    