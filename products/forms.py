from django import forms
from .models import ProductReview

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),  # 1 ile 5 arasında yıldız seçimi
            'comment': forms.Textarea(attrs={'rows': 4}),  # Yorum için metin alanı
        }




