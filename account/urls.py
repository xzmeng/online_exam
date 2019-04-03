from django.urls import path

from . import views

urlpatterns = [
    # path('test', views.test),
    path('accounts/register/', views.register, name='register'),
    path('', views.test)
]
