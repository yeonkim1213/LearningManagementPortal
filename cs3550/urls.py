"""
URL configuration for cs3550 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from grades import views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.assignments, name = 'assignments'),
    path("<int:assignment_id>/", views.assignment, name = 'index'),
    path("profile/login", views.login_form, name = 'login'),
    path("<int:assignment_id>/submissions", views.submissions, name = 'submissions'),
    path("profile/", views.profile, name = 'profile'),
    path("profile/login/", views.login_form, name = 'login'),
    path('profile/logout', views.logout_form, name='logout'),
    path('<int:assignment_id>/submit/', views.submit, name='submit'),
    path('<int:assignment_id>/grade/', views.grade, name='grade'),
    path('uploads/<str:filename>/', views.show_upload, name='show_upload'),
]
