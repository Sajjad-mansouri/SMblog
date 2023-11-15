from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

class CustomCreationForm(UserCreationForm):
	email=forms.EmailField()
	class Meta(UserCreationForm.Meta):
		model=get_user_model()
		fields=('username','email',)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['password1'].help_text=None