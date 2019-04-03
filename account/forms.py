from django.contrib.auth.models import User
from django import forms


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput)

    password2 = forms.CharField(label='重复密码',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)
        labels = {
            'username': "用户名"
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('两次密码不匹配！')
        return cd['password2']
