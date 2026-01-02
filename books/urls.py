from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_books, name='books'),
    path('add_book/', views.add_book, name='add_book'),
    path('delete<int:book_id>/', views.delete_book, name='delete_book'),
    path('edit<int:book_id>/', views.edit_book, name='edit_book'),
    path('<slug:slug>/', views.book_detail, name='book_detail'),
]
