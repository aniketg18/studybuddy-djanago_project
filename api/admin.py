from django.contrib import admin
from .models import Skill, Profile


#aniket80             ani18                   shra17               dha                  yokai               anti            troy            indian
#aniketuser80         anibuddy18              shrabuddy17          dhabuddy17           yokaiuser1          antiuser1       troyuser1       indianuser1
# Register your models here.
@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'location')
    search_fields = ('user__username', 'location')
    filter_horizontal = ('skills_known', 'skills_wanted')

