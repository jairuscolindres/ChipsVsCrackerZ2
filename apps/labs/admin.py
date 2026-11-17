from django.contrib import admin
from labs.models import Lab, Flag, Submission, Solve


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'points', 'is_published', 'created_at')
    list_filter = ('category', 'is_published', 'created_at')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('lab', 'flag_hash', 'is_case_sensitive', 'created_at')
    search_fields = ('lab__title', 'flag_hash')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('player', 'lab', 'submitted_flag', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'created_at')
    search_fields = ('player__username', 'lab__title', 'submitted_flag')


@admin.register(Solve)
class SolveAdmin(admin.ModelAdmin):
    list_display = ('player', 'lab', 'points_awarded', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('player__username', 'lab__title')
