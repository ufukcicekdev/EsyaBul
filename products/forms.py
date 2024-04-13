from django import forms
from .models import ProductReview, ProductRentalPrice,Product
from django.shortcuts import get_object_or_404

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),  # 1 ile 5 arasında yıldız seçimi
            'comment': forms.Textarea(attrs={'rows': 4}),  # Yorum için metin alanı
        }




class AddToCartForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput)
    price_type = forms.ChoiceField(
        choices=(('selling', 'Satın Alma'), ('rental', 'Kiralama')),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'price_type'})
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'name': 'quantity', 'value': '1'}),
        min_value=1,
        max_value=10,  # Örnek bir maksimum değer
        error_messages={
            'min_value': 'Miktar en az 1 olmalıdır.',
            'max_value': 'Miktar çok yüksek, lütfen daha düşük bir değer girin.'
        }
    )

    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id', None)
        super(AddToCartForm, self).__init__(*args, **kwargs)
        if product_id:
            rental_prices = ProductRentalPrice.objects.filter(product_id=product_id)
            rental_period_choices = [(price.id, price.name) for price in rental_prices]
            self.fields['rental_period'] = forms.ChoiceField(
                choices=rental_period_choices,
                widget=forms.Select(attrs={'class': 'form-control', 'id': 'rental_period'}),
                required=rental_prices.exists()  # Eğer rental_prices boş değilse rental_period zorunlu olacak
            )
            if rental_prices.count() == 0:
                self.fields['price_type'].choices = [('selling', 'Satın Alma')]  # Kiralama fiyatı yoksa price_type seçeneğini değiştir

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get('price_type')
        rental_period = cleaned_data.get('rental_period')

        if price_type == 'rental' and not rental_period:
            raise forms.ValidationError("Kiralama tipi seçildiği zaman kiralama süresi belirtmelisiniz.")

