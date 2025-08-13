import time
from django.utils.timezone import now
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import redirect
from django.template.loader import render_to_string

from notification.email_utils import send_email_threaded

def send_otp_email(user):
    try:
        send_email_threaded(
            subject='Account Login OTP Code',
            to_email=user.email,
            context={
                'name': user.get_full_name(),
                'code': user.otp.number
            },
            html_template='emails/login_otp_email.html'
        )
    except Exception as e:
        print(f"Failed to send OTP email: {e}")


def handle_successful_otp(request, user):
    """Handle post-OTP verification cleanup, login, and redirect."""

    # 1. Clear OTP-related session data
    for key in ['resend_count', 'otp_sent', 'last_resend_time']:
        request.session.pop(key, None)

    # 2. Reset OTP attempts for the next login cycle
    if hasattr(user, 'otp'):
        user.otp.attempts = 0
        user.otp.save(update_fields=['attempts'])  # Persist reset

    # 3. Send account access email (non-blocking if fails)
    try:
        message = render_to_string('emails/account_accessed_email.html', {
            'name': f'{user.first_name} {user.last_name}',
            'date': now()
        })
        # email_send('Account Login Confirmation', message, user.email)
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")

    # 4. Log the user in
    login(request, user)

    # 5. Redirect based on account status
    if user.status == "verified":
        messages.info(request, 'This account is not yet activated. Please contact the bank.')
        return redirect('account:login')

    elif user.status == "suspended":
        return redirect('customer:suspended')

    return redirect('customer:dashboard')


RESEND_COOLDOWN_SECONDS = 30
MAX_RESENDS_PER_SESSION = 5

def send_otp_with_cooldown(request, user):
    """
    Sends an OTP if cooldown has passed and max resend limit not reached.
    Returns one of: "sent", "cooldown", "max".
    """
    current_ts = time.time()
    last_resend_ts = request.session.get('last_resend_time')
    resend_count = request.session.get('resend_count', 0)

    # Check max resend limit
    if resend_count >= MAX_RESENDS_PER_SESSION:
        return "max"

    # Check cooldown
    if last_resend_ts and (current_ts - last_resend_ts) < RESEND_COOLDOWN_SECONDS:
        return "cooldown"

    # Cooldown passed → regenerate and send OTP
    user.otp.regenerate()
    send_otp_email(user)  # Ensure imported

    # Update session flags
    request.session['otp_sent'] = True
    request.session['last_resend_time'] = current_ts
    request.session['resend_count'] = resend_count + 1

    return "sent"


def handle_resend(request, user):
    """
    Handles OTP resending with cooldown & max resend restrictions.
    Can be used from both GET and POST flows.
    Returns an HttpResponseRedirect if action taken, else None.
    """
    now = time.time()
    resend_count = request.session.get('resend_count', 0)
    last_resend = request.session.get('last_resend_time', 0)

    # Check max resends
    if resend_count >= MAX_RESENDS_PER_SESSION:
        messages.error(request, "Maximum OTP resends reached. Please log in again.")
        request.session.flush()
        return redirect('account:login')

    # Check cooldown
    if now - last_resend < RESEND_COOLDOWN_SECONDS:
        remaining = int(RESEND_COOLDOWN_SECONDS - (now - last_resend))
        messages.warning(request, f"Please wait {remaining} seconds before requesting a new OTP.")
        return redirect('account:verify_otp')

    # Generate & send OTP
    user.otp.regenerate()
    send_otp_email(user)

    # Update session
    request.session['otp_sent'] = True
    request.session['resend_count'] = resend_count + 1
    request.session['last_resend_time'] = now

    # messages.success(request, "OTP sent to your email.")
    return redirect('account:verify_otp')


