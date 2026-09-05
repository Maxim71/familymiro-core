# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Agreement, VideoCapsule, AvatarEzhik, InteractiveComment, PunchListItem, BloggerUsage

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)

@admin.register(VideoCapsule)
class VideoCapsuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'video_title')
    search_fields = ('video_title',)

@admin.register(AvatarEzhik)
class AvatarEzhikAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')

@admin.register(InteractiveComment)
class InteractiveCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment_text')
    search_fields = ('comment_text',)

@admin.register(PunchListItem)
class PunchListItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'defect_description', 'is_fixed')
    list_filter = ('is_fixed',)
    search_fields = ('defect_description',)

@admin.register(BloggerUsage)
class BloggerUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'blogger_name', 'daily_limit')
    search_fields = ('blogger_name',)
