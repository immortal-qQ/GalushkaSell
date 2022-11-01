from django.contrib import admin
from django.contrib.auth.models import User
from mptt.admin import DraggableMPTTAdmin

from .models import *


class TgUserAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'nickname', 'vk_link', 'state')


admin.site.register(TgUser, TgUserAdmin)
admin.site.register(
    Category,
    DraggableMPTTAdmin,
    list_display=(
        'tree_actions',
        'indented_title',
    ),
    list_display_links=(
        'indented_title',
    ),
)
admin.site.register(Post, admin.ModelAdmin)
admin.site.register(FavouriteRecord, admin.ModelAdmin)

