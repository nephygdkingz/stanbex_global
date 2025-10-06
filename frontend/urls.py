from django.urls import path

from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.home_view, name="home"),
    path('about/', views.about_view, name="about"),
    path('contact-us/', views.contact_view, name="contact"),

    # password reset
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('password-reset/sent/', views.password_reset_sent, name='password-reset-sent'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset-password'),
    path('password-reset/success/', views.password_reset_success, name='password-reset-success'),
    path('password-reset/invalid/', views.password_reset_invalid, name='password-reset-invalid'),
]