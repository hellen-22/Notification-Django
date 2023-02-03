from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('home', views.home, name='home'),
    path('notifications', views.notifications, name='notifications'),
    path('add_notification', views.add_notification, name='add_notification'),
    path('notification_detail/<int:id>/', views.notification_detail, name='notification_detail'),
    path('notification_update/<int:pk>/', views.NotificationUpdate.as_view(), name='notification_update'),
    path('notification_delete/<int:pk>/', views.delete_notification, name='notification_delete')

]