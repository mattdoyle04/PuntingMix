from django.urls import path
from .views import ParentListView, MultiListView, LeaderboardView

app_name = 'ASPC'
urlpatterns = [
        # /ASPC/
        path('', ParentListView.as_view(), name='parent_list'),
        # /ASPC/detail/
        path('<int:pk>/', MultiListView.as_view(), name='multi_list'),
        # /ASPC/leaderboard/
        path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
        ]