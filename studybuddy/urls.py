"""
URL configuration for studybuddy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.views import home_page
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Default home route
    path('', home_page, name='home'),
    path('login/', views.login_view, name='login'), 
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # Profile page
    path('profile/', views.profile_view, name='profile'),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("change-password/", views.change_password_view, name="change_password"),
]


