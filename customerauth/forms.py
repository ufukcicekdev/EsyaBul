from django import forms
from django.contrib.auth.forms import UserCreationForm
from customerauth.models import User, Profile, Address
from phonenumber_field.formfields import PhoneNumberField
from cities_light.models import Country, City, Region, SubRegion
from products.models import RoomType, HomeType
from django.contrib.auth.password_validation import CommonPasswordValidator, MinimumLengthValidator, NumericPasswordValidator


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




class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Adınız"}))
    phone = PhoneNumberField(widget=forms.TextInput(attrs={"placeholder": "Telefon Numarası"}))  # PhoneNumberField'ı doğrudan formda kullanıyoruz.


    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'phone']


class AddressForm(forms.ModelForm):
 
    
    region = forms.ModelChoiceField(
        queryset=SubRegion.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='İlçe'
    )
    
    city = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='İl'
    )

    class Meta:
        model = Address
        fields = ['address_type', 'username', 'usersurname', 'phone', 'city', 'region', 
                  'address_name', 'address_line1', 'postal_code', 'firm_name','firm_taxcode','firm_tax_home']
        widgets = {
            'address_type': forms.RadioSelect(attrs={'class': 'radioButtons'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'usersurname': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
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
            'city': 'İlçe',
            'region': 'İl',
            'address_name': 'Adres Başlığı',
            'address_line1': 'Adres',
            'postal_code': 'Posta Kodu',
            'firm_name':'Firma Adı',
            'firm_taxcode':'Vergi Kodu',
            'firm_tax_home':'Vergi Dairesi'
        }
