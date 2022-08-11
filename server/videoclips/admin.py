from django.contrib import admin

from videoclips.models import Category, Reaction, UserReaction, VCBan, VCCategory, VCComment, VCReaction, VCSubscription, Videoclip

# @admin.register(Videoclip)


class VideoclipAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'create_date', 'get_categories']
    search_fields = ['title', 'description',
                     'categories__name', 'author__first_name']
    list_filter = ['author', 'create_date', 'categories']
    filter_horizontal = ('categories', )

    def get_categories(self, obj):
        return "\n".join([str(p) for p in obj.categories.all()])


admin.site.register(Category)
admin.site.register(Reaction)

admin.site.register(Videoclip, VideoclipAdmin)
admin.site.register(VCBan)
admin.site.register(VCCategory)
admin.site.register(VCComment)
admin.site.register(VCReaction)
admin.site.register(VCSubscription)

admin.site.register(UserReaction)
