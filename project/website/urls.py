from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('login/', login_view),
    path('register/', register_view)
]
