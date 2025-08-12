from django import forms

from .models import OtpCode

class CodeForm(forms.ModelForm):
	number = forms.CharField(label='OTP Code', help_text='Enter OTP code sent to your email.')

	class Meta:
		model = OtpCode
		fields = ['number',]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		for field in self.fields:
			self.fields[field].widget.attrs.update({'class': 'form-control'})