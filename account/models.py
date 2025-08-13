import random
from django.db import models
from django.contrib.auth.models import AbstractUser
# from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save

from .constants import GENDER_CHOICE, CURRENCY_CHOICE, STATUS_CHOICES, TRANSFER_CHOICES, TITLE_CHOICE, OTP_CHOICES
from .managers import UserManager

class MyUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, null=False, blank=False)
    title = models.CharField(max_length=8, choices=TITLE_CHOICE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    birth_date = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    created_on = models.DateField(null=True, blank=True)
    password_text = models.CharField(max_length=60, null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='verified')
    otp_status = models.CharField(max_length=100, choices=OTP_CHOICES, default='LOGIN OTP YES')
    transfer_status = models.CharField(max_length=100, choices=TRANSFER_CHOICES, default='Processing')



    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
	
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}-{self.email}'
    

class Profile(models.Model):
    user = models.OneToOneField(MyUser, related_name='profile', on_delete=models.CASCADE)
    # picture = CloudinaryField('image', null=True, default=None, blank=True)
    def __str__(self):
        return str(self.user)
    
def add_profile_post_save(sender, instance, created,*args, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
            )

post_save.connect(add_profile_post_save, sender=MyUser)


class BankAccountType(models.Model):
    name = models.CharField(max_length=128)
    maximum_withdraw = models.DecimalField(decimal_places=2, max_digits=14)
    minimum_withdraw = models.DecimalField(decimal_places=2, max_digits=14, default=1)

    def __str__(self):
        return self.name
    

class UserBankAccount(models.Model):
    user = models.OneToOneField(MyUser, related_name='account', on_delete=models.CASCADE)
    account_type = models.ForeignKey(BankAccountType,related_name='accounts', on_delete=models.CASCADE)
    account_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICE)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=14)
    street_address = models.CharField(max_length=512)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=256)

    def __str__(self):
        return self.user.get_full_name()
    

def user_account_post_save(sender, instance, created,*args, **kwargs):
    if created:
        nums = range(111111, 999999)
        f_nums = random.choices(nums, k=1)
        r = f_nums[0]
        final_r = str(int(r) + instance.id)
        instance.account_no = final_r[1:7]
        # instance.account_no = final_r[7:17] for posgres
        instance.save()

post_save.connect(user_account_post_save, sender=UserBankAccount)


class RequiredCode(models.Model):
    user = models.OneToOneField(MyUser, related_name='code', on_delete=models.CASCADE)
    code_name = models.CharField(max_length=100)
    code_number = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code_name

