import random
from django.db import models
from django.db.models.signals import post_save

from account.models import UserBankAccount
from .constants import TRANSACTION_TYPE_CHOICES, STATUS_CHOICES

class Transaction(models.Model):
	account = models.ForeignKey(UserBankAccount, related_name='transactions', on_delete=models.CASCADE)
	beneficiary_bank = models.CharField(max_length=200, blank=True)
	bank_address = models.CharField(max_length=200, blank=True)
	beneficiary_name = models.CharField(max_length=200)
	beneficiary_account = models.CharField(max_length=50, null=True, blank=True)
	beneficiary_address = models.CharField(max_length=200, blank=True)
	iban_number = models.CharField(max_length=100, blank=True, null=True)
	route_code = models.CharField(max_length=100)
	ref_code = models.CharField(max_length=200, null=True, blank=True)
	amount = models.DecimalField(max_digits=14, decimal_places=2)
	balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=14)
	description = models.CharField(max_length=200, blank=True)
	transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	date_created = models.DateTimeField(auto_now_add=True)
	transaction_date = models.DateField()
	transaction_time = models.TimeField()

	class Meta:
		ordering = ['-transaction_date', '-transaction_time']


	def save(self, *args, **kwargs):
		# Check if the route_code is empty or None
		if not self.route_code:
			self.route_code = 'SBDXTRY4563'
		super().save(*args, **kwargs)

	def __str__(self):
		return self.beneficiary_name


def route_code_post_save(sender, instance, created,*args, **kwargs):
	if created:
		ref = random.randint(0000, 9999)
		ref_code_f = int(ref) + instance.id
		instance.ref_code = f'SBGB{ref_code_f}'
		instance.save()

post_save.connect(route_code_post_save, sender=Transaction)