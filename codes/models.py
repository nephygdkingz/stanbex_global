from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
from django.utils.timezone import now, timedelta

from account.models import MyUser

class OtpCode(models.Model):
    number = models.CharField(max_length=10, blank=True)
    user = models.OneToOneField(MyUser, related_name='otp', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    OTP_EXPIRY_MINUTES = 5
    MAX_ATTEMPTS = 3

    def __str__(self):
        return str(self.number)

    def save(self, *args, **kwargs):
        """Generate a new random OTP and reset attempts."""
        number_list = [str(x) for x in range(10)]
        self.number = "".join(random.choice(number_list) for _ in range(8))
        self.created_at = now()
        self.attempts = 0
        super().save(*args, **kwargs)

    def is_expired(self):
        return (now() - self.created_at) > timedelta(minutes=self.OTP_EXPIRY_MINUTES)

    def has_attempts_left(self):
        return self.attempts < self.MAX_ATTEMPTS

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=['attempts'])


@receiver(post_save, sender=MyUser)
def generate_code_post_save(sender, instance, created, *args, **kwargs):
    if created:
        OtpCode.objects.create(user=instance)