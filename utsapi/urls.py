from django.urls import include, path
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token 
from django.conf.urls import url

router = routers.DefaultRouter()
router.register(r'files', views.FileViewSet)
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('current-user/', views.CurrentUser.as_view()),
    path('account/authentication/', views.AuthenticateUser.as_view()),
    path('account/change-password/', views.ChangePassword.as_view()),
    path('account/recovery-password/', views.RecoveryPassword.as_view()),
    path('files-project/', views.FilesFromProject.as_view()),
    path('recent-projects/', views.RecentProjects.as_view()),
    path('account/registration/', views.CreateUser.as_view()),
    path('account/logout/', views.LogoutUser.as_view()),
    path('files/favorites/<int:pk>/', views.FavoriteFiles.as_view()),
    path('download-file/<int:pk>/', views.DownloadFile.as_view()),
    # path('download/<int:pk>/', views.download_file, name='download_file'),
]