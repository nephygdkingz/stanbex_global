from django.contrib import admin
from .models import (MyUser, BankAccountType, UserBankAccount,
                    RequiredCode, Profile)

admin.site.register(MyUser)
admin.site.register(Profile)
admin.site.register(BankAccountType)
admin.site.register(UserBankAccount)
admin.site.register(RequiredCode)
