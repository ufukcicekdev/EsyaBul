from django import forms
from django.contrib.auth.forms import UserCreationForm
from customerauth.models import User, Profile, Address
from phonenumber_field.formfields import PhoneNumberField
from cities_light.models import Country, City, Region, SubRegion
from products.models import RoomType, HomeType
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm



class HomeTypeForm(forms.ModelForm):
    class Meta:
        model = HomeType
        fields = ['name', 'image']



class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Kullanıcı Adı"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder":"Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Şifreniz"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Tekrar Şifreniz"}))

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if len(password1) < 8:
            raise forms.ValidationError('Şifreniz en az 8 karakter uzunluğunda olmalıdır.')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Şifreler eşleşmiyor.')

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
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', "type":"number"}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        # Telefon numarası sadece sayısal karakterler içermeli
        if not phone.isdigit():
            raise forms.ValidationError('Telefon numarası yalnızca sayısal karakterler içermelidir.')

        return phone

   
    



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
        queryset=Region.objects.all().order_by('name'),
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





