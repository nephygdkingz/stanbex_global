from django.urls import path

from . import views

app_name = 'account'

urlpatterns = [
    path('register/', views.registerUser, name='register'),
    path('login/', views.loginUser, name='login'),
    path('verify_otp/', views.verifyOtp, name='verify_otp'),
    path('resend-otp/', views.resendOtp, name='resend_otp'),
    path('logout/', views.logoutUser, name='logout'),
]