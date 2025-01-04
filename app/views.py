from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from app.serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer,
    FriendRequestSerializer,
    UserSerializer,
    UserPostSerializer,
    GlobalFeedPostSerializer,
    CommentSerializer,
    LikeSerializer,
    UserProfileSerializer,
    FriendshipSerializer
)
from django.contrib.auth import authenticate
from app.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import FriendRequest, Friendship, User,Like, Comment, Save
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.cache import cache
from django.utils import timezone
from .models import UserPost
from datetime import timedelta
from rest_framework import generics, permissions
from .models import User


def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
      'email': user.email, 
  }

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    print(serializer)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        to_user = get_object_or_404(User, id=to_user_id)
        # print("this is to_user",to_user)
        from_user = request.user
        # print("this is from_user", from_user)

        # Check if from_user and to_user are same
        if from_user == to_user:
            return Response({'error': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if friend request already sent
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already friends
        if Friendship.objects.filter(Q(user1=from_user, user2=to_user) | Q(user1=to_user, user2=from_user)).exists():
            return Response({'error': 'You are already friends.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check limit
        cache_key = f'friend_request_count_{from_user.id}'
        friend_request_count = cache.get(cache_key, 0)

        if friend_request_count >= 20:
            return Response({'error': 'You cannot send more than 3 friend requests within a minute.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Save friend request
        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()

        # Update limit count
        cache.set(cache_key, friend_request_count + 1, timeout=60) 

        return Response({'msg': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        friend_request_id = request.data.get('friend_request_id')
        friend_request = get_object_or_404(FriendRequest, id=friend_request_id)

        if friend_request.to_user != request.user:
            return Response({'error': 'You cannot accept this friend request.'}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.accepted = True
        friend_request.save()
        Friendship.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)
        return Response({'msg': 'Friend request accepted.'}, status=status.HTTP_200_OK)

class RejectFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        friend_request_id = request.data.get('friend_request_id')
        friend_request = get_object_or_404(FriendRequest, id=friend_request_id)
        if friend_request.to_user != request.user:
            return Response({'error': 'You cannot reject this friend request.'}, status=status.HTTP_400_BAD_REQUEST)
        friend_request.rejected = True
        friend_request.save()
        return Response({'msg': 'Friend request rejected.'}, status=status.HTTP_200_OK)

class FriendRequestListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        friend_requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FriendListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        friendships = Friendship.objects.filter(Q(user1=user) | Q(user2=user))
        friends = []
        for friendship in friendships:
            friend = friendship.user1 if friendship.user2 == user else friendship.user2
            friends.append(friend)
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        friend_id = kwargs.get('friend_id') 
        
        try:
            friend = User.objects.get(id=friend_id)
        except User.DoesNotExist:
            return Response({"detail": "Friend not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the friendship have or not
        friendship = Friendship.objects.filter(
            (Q(user1=user) & Q(user2=friend)) | (Q(user1=friend) & Q(user2=user))
        ).first()

        if friendship:
            friendship.delete()  # Remove the friendship
            return Response({"detail": "Friend removed successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Friendship does not exist"}, status=status.HTTP_400_BAD_REQUEST)

class UserSearchAPIView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request, *args, **kwargs):
        search_keyword = request.query_params.get('q', '')
        # print(search_keyword)
        users_by_email = User.objects.filter(email=search_keyword)
        users_by_name = User.objects.filter(name__icontains=search_keyword)
        users = users_by_email | users_by_name
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user_posts = UserPost.objects.filter(user=request.user).order_by('-created_at')
        serializer = UserPostSerializer(user_posts, many=True)
        return Response(serializer.data)

class GlobalPostsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        global_posts = UserPost.objects.exclude(user=request.user).order_by('-created_at')
        serializer = GlobalFeedPostSerializer(global_posts, many=True)
        return Response(serializer.data)

class LikePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = UserPost.objects.get(id=post_id)
        Like.objects.get_or_create(user=request.user, post=post)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        post = UserPost.objects.get(id=post_id)
        Like.objects.filter(user=request.user, post=post).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, post_id):
        post = UserPost.objects.get(id=post_id)
        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentPostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = UserPost.objects.get(id=post_id)
        except UserPost.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SavePostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved_posts = Save.objects.filter(user=request.user).values_list('post', flat=True)
        posts = UserPost.objects.filter(id__in=saved_posts)
        serializer = UserPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, post_id):
        try:
            post = UserPost.objects.get(id=post_id)
        except UserPost.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        Save.objects.create(user=request.user, post=post)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        saves = Save.objects.filter(user=request.user, post__id=post_id)
        if saves.exists():
            saves.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class SharePostView(APIView):
    def post(self, request, post_id):
        try:
            post = UserPost.objects.get(id=post_id)
            share_url = f"http://127.0.0.1:8000/api/user/posts/{post.id}"  # Create the shareable URL
            
            # You might want to format the content for sharing
            share_content = {
                'message': f"Check out this post: {post.content}",
                'url': share_url,
                'image': post.image.url if post.image else None,  # URL of the image if it exists
            }
            return Response(share_content, status=status.HTTP_200_OK)
        except UserPost.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)