from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.conf import settings

class UserManager(BaseUserManager):

    def create_user(self, email, name, tc, password=None, password2=None):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=email,
            name=name,
            tc=tc,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):

        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    RELATIONSHIP_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('engaged', 'Engaged'),
        ('in_relationship', 'In a Relationship'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
    ]

    email = models.CharField(verbose_name='Email', max_length=255, unique=True)
    name = models.CharField(max_length=200)
    tc = models.BooleanField()  # Terms and Conditions accepted
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_pic = models.ImageField(upload_to='cover_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # New fields
    location = models.CharField(max_length=255, blank=True, null=True)  # Location of the user
    work = models.CharField(max_length=255, blank=True, null=True)       # Work information
    study = models.CharField(max_length=255, blank=True, null=True)      # Study information
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_STATUS_CHOICES,
        default='single',
    )
    date_of_birth = models.DateField(blank=True, null=True)  # Date of birth field

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tc']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        # All admins are staff
        return self.is_admin

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_friend_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"

class Friendship(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user1} & {self.user2}"

class UserPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user} on {self.created_at}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.created_at}"

class Save(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='saves', on_delete=models.CASCADE)
    post = models.ForeignKey(UserPost, related_name='saves', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
