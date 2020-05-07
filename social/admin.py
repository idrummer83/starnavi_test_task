from django.contrib import admin

# Register your models here.

from .models import StarnaviUser


@admin.register(StarnaviUser)
class UserAdmin(admin.ModelAdmin):
    pass