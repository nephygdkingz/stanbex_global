import time
from django.utils.timezone import now
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.template.loader import render_to_string
# from .email_service import email_send

def send_otp_email(user):
    """Send OTP email to the user."""
    try:
        message = render_to_string('emails/login_otp_email.html', {
            'name': f'{user.first_name} {user.last_name}',
            'code': user.otp.number
        })
        # email_send('Account Login OTP Code', message, user.email)
    except Exception as e:
        print(f"Failed to send OTP email: {e}")


def handle_successful_otp(request, user):
    """Handle what happens after a successful OTP verification."""
    try:
        message = render_to_string('emails/account_accessed_email.html', {
            'name': f'{user.first_name} {user.last_name}',
            'date': now()
        })
        # email_send('Account Login Confirmation', message, user.email)
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

    if user.status == "verified":
        messages.info(request, 'This account is not yet activated. Please contact the bank.')
        return redirect('account:verify_otp')

    elif user.status == "suspended":
        user.otp.save()  # regenerate OTP for next login
        login(request, user)
        return redirect('customer:suspended')

    else:
        user.otp.save()  # regenerate OTP for next login
        login(request, user)
        return redirect('customer:customer_dashboard')
    

RESEND_COOLDOWN_SECONDS = 30
MAX_RESENDS_PER_SESSION = 5

def send_otp_with_cooldown(request, user):
    """
    Sends an OTP to the user if cooldown has passed.
    Returns True if OTP sent, False if blocked by cooldown.
    """
    current_ts = time.time()
    last_resend_ts = request.session.get('last_resend_time')

    # Cooldown check
    if last_resend_ts and (current_ts - last_resend_ts) < RESEND_COOLDOWN_SECONDS:
        remaining = int(RESEND_COOLDOWN_SECONDS - (current_ts - last_resend_ts))
        messages.warning(request, f"Please wait {remaining} seconds before requesting a new OTP.")
        return False

    # Cooldown passed → regenerate and send OTP
    user.otp.regenerate()
    send_otp_email(user)  # make sure this is imported

    # Update session flags
    request.session['otp_sent'] = True
    request.session['last_resend_time'] = current_ts

    messages.success(request, "A new OTP has been sent to your email.")
    return True