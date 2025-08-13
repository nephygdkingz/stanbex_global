from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string

from .models import MyUser
from .forms import (UserBankAccountForm, UserRegistrationForm)
from codes.forms import CodeForm
from .utils import send_otp_email, handle_successful_otp

def registerUser(request):
    if request.method == 'POST':
        registration_form = UserRegistrationForm(request.POST)
        address_form = UserBankAccountForm(request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save(commit=False)
            user.password_text = registration_form.cleaned_data['password1']
            user.save()
            address = address_form.save(commit=False)
            address.user = user 
            address.save()			

            messages.info(request, 'Your account was created successfully, it is now awaiting activation....')
            if request.user.is_authenticated:
                return redirect('account:account_holders')
            else:
                return redirect('account:register')
    else:
        registration_form = UserRegistrationForm()
        address_form = UserBankAccountForm()

    context = {'form':registration_form , 'ad_form':address_form}
    return render(request, 'account/register.html', context)


def loginUser(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('account:admin_dashboard')
            else:
                if user.otp_status == 'LOGIN OTP YES':
                    request.session['pk'] = user.pk
                    return redirect('account:verify_otp')
                else:
                    if user.status == "verified":
                        messages.info(request, 'This account is not yet activated, Please contact our customer care for more information')
                        return redirect('frontend:home')
                    elif user.status == "suspended":
                        login(request, user)
                        return redirect('customer:suspended')
                    
                    else:
                        login(request, user)
                        return redirect('customer:customer_dashboard')
                
        else:
            messages.error(request, 'Username or Password is incorrect')
    return render(request, 'account/login.html')


def verifyOtp(request):
    pk = request.session.get('pk')
    if not pk:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('account:login')

    user = get_object_or_404(MyUser, id=pk)
    form = CodeForm(request.POST or None)

    # Only send OTP once per session unless regenerated
    if request.method == "GET" and not request.session.get('otp_sent', False):
        user.otp.regenerate()  # generates code & resets attempts
        send_otp_email(user)
        request.session['otp_sent'] = True

    if request.method == "POST" and form.is_valid():
        entered_code = str(form.cleaned_data.get('number'))

        if user.otp.is_expired():
            messages.error(request, "OTP expired. A new code has been sent.")
            user.otp.regenerate()
            send_otp_email(user)
            return redirect('account:verify_otp')

        if not user.otp.has_attempts_left():
            messages.error(request, "Too many failed attempts. A new OTP has been sent to your email.")
            user.otp.regenerate()
            send_otp_email(user)
            return redirect('account:verify_otp')

        if entered_code == user.otp.number:
            return handle_successful_otp(request, user)
        else:
            user.otp.increment_attempts()
            remaining = user.otp.MAX_ATTEMPTS - user.otp.attempts
            messages.error(request, f"Incorrect OTP. Please check the code and try again.")
            # messages.error(request, f"Incorrect OTP. {remaining} attempt(s) left.")
            return redirect('account:verify_otp')

    return render(request, 'account/verify_otp.html', {
        'form': form,
        'email': user.email
    })


def resendOtp(request):
    pk = request.session.get('pk')
    if not pk:
        messages.error(request, "Session expired. Please log in again.")
        return redirect('account:login')

    user = get_object_or_404(MyUser, id=pk)
    user.otp.regenerate()
    send_otp_email(user)
    request.session['otp_sent'] = True
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('account:verify_otp')
