from django.urls import path
from app.views import (
    UserLoginView,
    UserProfileView,
    UserProfileUpdateView,
    UserRegistrationView,
    SendFriendRequestView,
    AcceptFriendRequestView,
    RejectFriendRequestView,
    FriendRequestListView,
    FriendListView,
    UserSearchAPIView,
    UserPostsAPIView,
    GlobalPostsAPIView,
    LikePostAPIView,
    CommentPostAPIView,
    SavePostAPIView,
    SharePostView
)

urlpatterns = [

    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('send-friend-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('accept-friend-request/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('reject-friend-request/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('friend-requests/', FriendRequestListView.as_view(), name='friend-requests'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('friends/<int:friend_id>/', FriendListView.as_view(), name='unfriend'),
    path('search/', UserSearchAPIView.as_view(), name='search'),
    path('userposts/', UserPostsAPIView.as_view(), name='user-posts'),
    path('globalposts/', GlobalPostsAPIView.as_view(), name='global-posts'), 
    path('posts/<int:post_id>/like/', LikePostAPIView.as_view(), name='like-post'),
    path('posts/<int:post_id>/comment/', CommentPostAPIView.as_view(), name='comment-post'),
    path('posts/<int:post_id>/share/', SharePostView.as_view(), name='share-post'),
    path('posts/<int:post_id>/save/', SavePostAPIView.as_view(), name='save-post'),
    path('saved-posts/',SavePostAPIView.as_view(),name='saved-posts'),
]


