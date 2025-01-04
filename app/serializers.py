from rest_framework import serializers
from app.models import User, FriendRequest, Friendship, UserPost, Like, Comment, Save
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions

class UserRegistrationSerializer(serializers.ModelSerializer):
  password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
  class Meta:
    model = User
    fields=['email', 'name', 'password', 'password2', 'tc']
    extra_kwargs={
      'password':{'write_only':True}
    }

  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    return attrs

  def create(self, validate_data):
    return User.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
  email = serializers.CharField(max_length=255)
  class Meta:
    model = User
    fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'name', 
            'email', 
            'bio', 
            'profile_pic', 
            'cover_pic', 
            'location',         
            'study',           
            'relationship_status', 
            'date_of_birth' ,
            'created_at'    
        ]
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'name', 
            'email', 
            'tc', 
            'profile_pic', 
            'cover_pic', 
            'bio', 
            'location',        
            'work',            
            'study',           
            'relationship_status', 
            'date_of_birth'    ,
            'created_at'
        ]
        read_only_fields = ['email']  # Email remains read-only

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.tc = validated_data.get('tc', instance.tc)

        # Handle image updates
        if 'profile_pic' in validated_data:
            instance.profile_pic = validated_data['profile_pic']
        if 'cover_pic' in validated_data:
            instance.cover_pic = validated_data['cover_pic']

        # Update new fields
        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)  # Updated field
        instance.work = validated_data.get('work', instance.work)  # Updated field
        instance.study = validated_data.get('study', instance.study)  # Updated field
        instance.relationship_status = validated_data.get('relationship_status', instance.relationship_status)  # Updated field
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)  # Updated field

        instance.save()
        return instance

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()
    to_user = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'accepted', 'rejected']

class FriendshipSerializer(serializers.ModelSerializer):
    user1 = UserSerializer()
    user2 = UserSerializer()

    class Meta:
        model = Friendship
        fields = ['id', 'user1', 'user2', 'created']

class UserPostSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()
    user = UserSerializer()

    class Meta:
        model = UserPost
        fields = ['id', 'user', 'content', 'image', 'created_at']

class GlobalFeedPostSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()
    user = UserSerializer()

    class Meta:
        model = UserPost
        fields = ['id', 'user', 'content', 'image', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True) 
    email = serializers.StringRelatedField(source='user', read_only=True) 
    profile_pic = serializers.ImageField(source='user.profile_pic', read_only=True)
    user = UserSerializer()

    class Meta:
        model = Like
        fields = ['id', 'user', 'email', 'post', 'created_at', 'profile_pic'] 

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['content','user']

class SaveSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    user = UserSerializer()

    class Meta:
        model = Save
        fields = ['id', 'user', 'post', 'created_at']