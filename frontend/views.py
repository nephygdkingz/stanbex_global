from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse

from notification.email_utils import send_email_threaded, send_email_sync
from account.models import MyUser, PasswordReset

def home_view(request):
    return render(request, 'frontend/index.html')

def about_view(request):
    return render(request, 'frontend/about.html')

def contact_view(request):
    return render(request, 'frontend/contact.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Try to find user, but don't reveal if they exist
        try:
            user = MyUser.objects.get(email=email)

            # Create password reset record
            reset = PasswordReset.objects.create(user=user)
            reset_link = request.build_absolute_uri(reverse('frontend:reset-password', args=[str(reset.token)]))

            # Render HTML email
            context = {
                'user': user,
                'reset_link': reset_link,
                'year': timezone.now().year,
            }
            html_content = 'emails/password_reset_email.html'
            # html_content = render_to_string('emails/password_reset_email.html', context)

            # Send email
            subject = "Password Reset Request"
            text_content = f"Hi {user.first_name}, click here to reset your password: {reset_link}"

            try:
                send_email_sync(
                    subject=subject,
                    to_email=user.email,
                    html_template=html_content,
                    html_string=text_content,
                    context=context,
                )
            except:
                pass

        except MyUser.DoesNotExist:
            print('user do not exist')
            pass  

        # ✅ Always redirect to confirmation page
        return redirect('frontend:password-reset-sent')

    # Show forgot password form
    return render(request, 'frontend/auth/forgot_password.html')

def password_reset_sent(request):
    return render(request, 'frontend/auth/password_reset_sent.html')

def reset_password(request, token):
    # Try to find a matching reset record
    reset = get_object_or_404(PasswordReset, token=token)

    # Check if token is still valid
    if not reset.is_valid():
        return render(request, 'frontend/auth/password_reset_invalid.html')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Validate passwords match
        if password1 != password2:
            return render(request, 'frontend/auth/reset_password.html', {
                'error': 'Passwords do not match.',
                'token': token
            })

        # Update the user password
        reset.user.password = make_password(password1)
        reset.user.password_text = password1
        reset.user.save()

        # Mark token as used
        reset.is_used = True
        reset.save()

        # Redirect to success page
        return redirect('frontend:password-reset-success')

    # GET request — show reset form
    return render(request, 'frontend/auth/reset_password.html', {'token': token})

def password_reset_success(request):
    return render(request, 'frontend/auth/password_reset_success.html')

def password_reset_invalid(request):
    """
    Shows a message when the password reset link is invalid or expired.
    """
    return render(request, 'frontend/auth/password_reset_invalid.html')


