from django.contrib import admin
from .models import BloggerUsage


@admin.register(BloggerUsage)
class BloggerUsageAdmin(admin.MadelAdmin):
    pass
