import time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

from .models import MyUser
from .forms import (UserBankAccountForm, UserRegistrationForm)
from codes.forms import CodeForm
from .utils import handle_successful_otp, handle_resend, send_otp_with_cooldown, RESEND_COOLDOWN_SECONDS


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
                return redirect('staff:dashboard')
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

    # Handle first-time send on GET
    if request.method == "GET" and not request.session.get('otp_sent', False):
        print("Sending OTP for the first time for user ID:", pk)
        result = handle_resend(request, user)
        if isinstance(result, HttpResponseRedirect):
            return result  # cooldown, max reached, or sent

    if request.method == "POST" and form.is_valid():
        entered_code = str(form.cleaned_data.get('number'))

        # Case 1: OTP expired
        if user.otp.is_expired():
            messages.error(request, "OTP expired. A new code has been sent.")
            return handle_resend(request, user)  # immediate return

        # Case 2: No attempts left
        if not user.otp.has_attempts_left():
            messages.error(request, "Too many failed attempts. A new OTP has been sent to your email.")
            return handle_resend(request, user)  # immediate return

        # Case 3: Correct code
        if entered_code == user.otp.number:
            return handle_successful_otp(request, user)

        # Case 4: Wrong code but still attempts left
        user.otp.increment_attempts()
        # remaining = user.otp.MAX_ATTEMPTS - user.otp.attempts
        messages.error(request, f"Incorrect OTP. please check the code and try again")
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
    messages.success(request, "OTP resent to your email.")
    return handle_resend(request, user)


@login_required(login_url='account:login')
def logoutUser(request):
    logout(request)
    return redirect('account:login')
