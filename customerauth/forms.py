from django import forms
from django.contrib.auth.forms import UserCreationForm
from customerauth.models import User, Profile, Address
from phonenumber_field.formfields import PhoneNumberField
from cities_light.models import Country, City, Region
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
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    city = forms.ModelChoiceField(
        queryset=City.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    region = forms.ModelChoiceField(
        queryset=Region.objects.all().order_by('name'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Address
        fields = ['address_type', 'name', 'city', 'country', 'region', 'address_line1', 'address_line2', 'state', 'postal_code']
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
