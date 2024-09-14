from django import forms
from django.contrib.auth.forms import UserCreationForm
from customerauth.models import User, Address
from phonenumber_field.formfields import PhoneNumberField
from cities_light.models import Country, City, Region, SubRegion
from products.models import RoomType, HomeType
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.core.exceptions import ValidationError
import re
from customerauth.send_confirmation import send_confirmation_email
from django.core.validators import EmailValidator
from django.contrib.auth import authenticate

class HomeTypeForm(forms.ModelForm):
    class Meta:
        model = HomeType
        fields = ['name', 'image']



class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Kullanıcı Adı"}),
        label="Kullanıcı Adı"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
        label="Email"
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Şifreniz"}),
        label="Şifre"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Tekrar Şifreniz"}),
        label="Şifre Tekrar"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Bu e-posta adresi zaten kayıtlı.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError('Şifreniz en az 8 karakter uzunluğunda olmalıdır.')
        if not re.search(r'[A-Z]', password1):
            raise ValidationError('Şifreniz en az bir büyük harf içermelidir.')
        if not re.search(r'[a-z]', password1):
            raise ValidationError('Şifreniz en az bir küçük harf içermelidir.')
        if not re.search(r'[0-9]', password1):
            raise ValidationError('Şifreniz en az bir rakam içermelidir.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Şifreler eşleşmiyor.')

        return password2



class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['receive_email_notifications', 'receive_sms_notifications']
        widgets = {
            'receive_email_notifications': forms.CheckboxInput(),
            'receive_sms_notifications': forms.CheckboxInput(),
        }




class ProfileForm(forms.ModelForm):
    tckn = forms.CharField(
        label='TC Kimlik No',
        max_length=11,
        min_length=11,
        widget=forms.TextInput(attrs={"class": "form-control", "type": "number"})
    )
    birth_date = forms.DateField(
        label='Doğum Tarihi',
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'})
    )
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'tckn', 'birth_date']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', "type": "number"}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.isdigit():
            raise forms.ValidationError('Telefon numarası yalnızca sayısal karakterler içermelidir.')

        return phone

    def clean_tckn(self):
        tckn = self.cleaned_data.get('tckn')

        if not tckn.isdigit():
            raise forms.ValidationError('TC Kimlik No yalnızca sayısal karakterler içermelidir.')

        if len(tckn) != 11:
            raise forms.ValidationError('TC Kimlik No 11 haneli olmalıdır.')
        
        if User.objects.filter(tckn=tckn).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Bu TC Kimlik No zaten başka bir kullanıcı tarafından kullanılıyor.')

        return tckn

   
    



class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['placeholder'] = 'Mevcut Şifre'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Yeni Şifre'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Yeni Şifreyi Tekrar Girin'



class AddressForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(AddressForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['firm_name'].required = False
        self.fields['firm_taxcode'].required = False
        self.fields['firm_tax_home'].required = False


    city = forms.ModelChoiceField(
        queryset=Region.objects.filter(name='Istanbul').order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='İl', required=True
    )

    class Meta:
        model = Address
        fields = ['address_type', 'username', 'usersurname', 'phone', 'city', 'region',
                  'address_name', 'address_line1', 'postal_code', 'firm_name','firm_taxcode','firm_tax_home']
        widgets = {
            'address_type': forms.RadioSelect(attrs={'class': 'radioButtons'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'usersurname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'type':"number"}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'address_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'firm_name': forms.TextInput(attrs={'class': 'form-control'}),
            'firm_taxcode': forms.TextInput(attrs={'class': 'form-control'}),
            'firm_tax_home': forms.TextInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'address_type': 'Fatura Tipi',
            'username': 'Ad',
            'usersurname': 'Soyad',
            'phone': 'Telefon Numarası',
            'city': 'İl',
            'region': 'İlçe',
            'address_name': 'Adres Başlığı',
            'address_line1': 'Adres',
            'postal_code': 'Posta Kodu',
            'firm_name':'Firma Adı',
            'firm_taxcode':'Vergi Kodu',
            'firm_tax_home':'Vergi Dairesi'
        }

    def clean(self):
        cleaned_data = super().clean()
        address_type = cleaned_data.get('address_type')

        if address_type == 2:
            firm_name = cleaned_data.get('firm_name')
            if not firm_name:
                self.add_error('firm_name', 'Firma Adı zorunludur.')

            firm_taxcode = cleaned_data.get('firm_taxcode')
            if not firm_taxcode:
                self.add_error('firm_taxcode', 'Firma Vergi Kodu zorunludur.')

            firm_tax_home = cleaned_data.get('firm_tax_home')
            if not firm_tax_home:
                self.add_error('firm_tax_home', 'Firma Vergi Dairesi zorunludur.')

        return cleaned_data




class CancelOrderForm(forms.Form):
    reason = forms.CharField(label="İptal Nedeni", widget=forms.Textarea(attrs={'required': True, 'class': 'form-control'}))




class EmailChangeForm(forms.Form):
    new_email = forms.EmailField(label='Yeni E-posta Adresi', widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(label='Mevcut Şifre', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    old_email = forms.EmailField(widget=forms.HiddenInput()) 

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['old_email'].initial = user.email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not authenticate(username=self.user.email, password=password):
            raise forms.ValidationError('Mevcut şifreniz yanlış.')
        return password

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('Bu e-posta adresi başka bir hesap tarafından kullanılıyor.')
        return new_email

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        old_email = cleaned_data.get('old_email')

        if new_email and old_email and new_email == old_email:
            self.add_error('new_email', 'Yeni e-posta adresi eski e-posta adresinizle aynı olamaz.')

        return cleaned_data






class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='E-posta Adresiniz', widget=forms.EmailInput(attrs={'placeholder': 'E-posta adresinizi girin...'}))

class SetNewPasswordForm(forms.Form):
    otp = forms.CharField(
        label='Doğrulama Kodu',
        widget=forms.TextInput(attrs={
            'placeholder': 'Doğrulama kodunu girin...',
            'autocomplete': 'off'  
        })
    )
    new_password = forms.CharField(
        label='Yeni Şifreniz',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Yeni şifrenizi girin...',
            'autocomplete': 'new-password' 
        })
    )