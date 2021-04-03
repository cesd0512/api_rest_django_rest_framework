from django.urls import include, path
from rest_framework import routers
from . import views
from rest_framework.authtoken.views import obtain_auth_token 
from django.conf.urls import url
from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register(r'files', views.FileViewSet)
router.register(r'projects', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'), #autenticacion basica"""
    # path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'), #JWT
    # path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'), #JWT
    # ----------
    path('current-user/', views.CurrentUser.as_view()),
    path('account/authentication/', views.AuthenticateUser.as_view()),
    path('account/change-password/', views.ChangePassword.as_view()),
    path('account/recovery-password/', views.RecoveryPassword.as_view()),
    path('account/security/', views.UpdateSecurityAccount.as_view()),
    path('files-project/', views.FilesFromProject.as_view()),
    path('recent/projects/', views.RecentProjects.as_view()),
    path('recent/files/', views.RecentDownloadFiles.as_view()),
    path('account/registration/', views.CreateUser.as_view()),
    path('account/update/', views.UpdateUser.as_view()),
    path('account/logout/', views.LogoutUser.as_view()),
    path('files/favorites/<int:pk>/', views.UpdateFavoriteFiles.as_view()),
    path('files_favorites/', views.FavoriteFiles.as_view()),
    path('download-file/<int:pk>/', views.DownloadFile.as_view()),
    path('total/indicators/', views.TotalsIndicatorsView.as_view()),
    path('month/indicators/', views.MonthsIndicatorsView.as_view()),
    # path('download/<int:pk>/', views.download_file, name='download_file'),
]