from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import random

from account.models import MyUser

# Create your models here.
class OtpCode(models.Model):
    number = models.CharField(max_length=5, blank=True)
    user = models.OneToOneField(MyUser, related_name='otp', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.number)

    def save(self, *args, **kwargs):
        number_list = [x for x in range(10)]
        code_items = []

        for i in range(5):
            num = random.choice(number_list)
            code_items.append(num)

        code_string = "".join(str(item) for item in code_items)
        self.number = code_string
        super().save(*args, **kwargs)


@receiver(post_save, sender=MyUser)
def generate_code_post_save(sender, instance, created, *args, **kwargs):
    if created:
        OtpCode.objects.create(user=instance)