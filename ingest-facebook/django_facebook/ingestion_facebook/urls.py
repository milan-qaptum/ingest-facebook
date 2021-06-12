from django.urls import path, include
from . import views

urlpatterns = [
    path('facebook/',views.facebook_function),
    path('facebook/checkuser/',views.facebook_checkUser),
]
