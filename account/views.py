from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import (UserBankAccountForm, UserRegistrationForm)

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
