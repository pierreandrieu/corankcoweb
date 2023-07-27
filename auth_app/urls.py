from django.urls import path, include
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('confirm/<str:token>', views.confirm_view, name='confirm'),
    path('accounts/', include('allauth.urls')),
]
