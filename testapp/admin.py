from django.contrib import admin

from .models import Article, Author


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("author", "title")
