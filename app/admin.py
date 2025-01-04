from django.contrib import admin
from app.models import User, UserPost, Friendship, FriendRequest, Like, Comment, Save
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

class UserModelAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'tc', 'is_admin', 'display_profile_pic', 'display_cover_pic', 'display_bio')
    list_filter = ('is_admin',)
    fieldsets = (
        ('User Credentials', {'fields': ('email', 'password')}), 
        ('Personal info', {'fields': ('name', 'tc', 'bio', 'profile_pic', 'cover_pic')}), 
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'tc', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email', 'id')
    filter_horizontal = ()

    def display_profile_pic(self, obj):
        if obj.profile_pic:
            return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50%;" />', obj.profile_pic.url)
        return format_html('<img src="/media/path/to/default_profile_pic.jpg" style="width: 50px; height: 50px; border-radius: 50%;" />')

    display_profile_pic.short_description = 'Profile Picture'

    def display_cover_pic(self, obj):
        if obj.cover_pic:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.cover_pic.url)
        return format_html('<img src="/media/path/to/default_cover_pic.jpg" style="width: 100px; height: 100px;" />')

    display_cover_pic.short_description = 'Cover Picture'

    def display_bio(self, obj):
        return obj.bio or 'No bio available'

    display_bio.short_description = 'Bio'

admin.site.register(User, UserModelAdmin)  # Register User model

# Register UserPost model
@admin.register(UserPost)
class UserPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    list_filter = ('user',)
    search_fields = ('content',)
    ordering = ('-created_at',)

# Register Friendship model
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created')
    list_filter = ('created',)
    ordering = ('-created',)

# Register FriendRequest model
@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'accepted', 'rejected', 'timestamp')
    list_filter = ('accepted', 'rejected',)
    ordering = ('-timestamp',)

# Register Like model
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('user', 'post',)
    ordering = ('-created_at',)

# Register Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at')
    list_filter = ('user', 'post',)
    ordering = ('-created_at',)

# Register Save model
@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('user', 'post',)
    ordering = ('-created_at',)
