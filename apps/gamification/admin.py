from django.contrib import admin

from .models import Badge, GamificationProfile, Mission, MissionStep, PointsLog, UserBadge, UserMissionProgress


@admin.register(GamificationProfile)
class GamificationProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'level', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'is_active', 'is_compliance')
    search_fields = ('code', 'name')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_at')
    list_filter = ('badge',)


class MissionStepInline(admin.TabularInline):
    model = MissionStep
    extra = 0


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'is_active', 'order', 'bonus_points')
    inlines = [MissionStepInline]


@admin.register(PointsLog)
class PointsLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'points', 'reference', 'created_at')
    list_filter = ('source',)
    readonly_fields = ('created_at',)


@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'mission', 'is_completed', 'completed_at')
