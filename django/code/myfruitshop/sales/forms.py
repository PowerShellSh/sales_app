from django import forms
from django.core.exceptions import ValidationError
from .models import Sale, Fruit
from typing import Dict, Any, Union

class FruitForm(forms.ModelForm):
    class Meta:
        model = Fruit
        fields = ['name', 'price']

    def clean_price(self) -> float:
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("単価は正の数で入力してください。")
        return price

    def non_field_errors(self) -> list[str]:
        errors = super().non_field_errors()
        if '__all__' in self.errors:
            errors.extend(self.errors['__all__'])
        return errors

class SaleAddForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['fruit', 'quantity', 'sale_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # クエリセットをis_active=Trueにフィルタリング
        self.fields['fruit'].queryset = Fruit.objects.filter(is_active=True)

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        fruit = cleaned_data.get('fruit')
        quantity = cleaned_data.get('quantity')

        # Fruitが存在するか確認
        try:
            fruit_instance = Fruit.objects.get(name=fruit)
        except Fruit.DoesNotExist:
            raise forms.ValidationError('Selected fruit does not exist.')

        return cleaned_data

class SaleCombinedForm(forms.ModelForm):
    total_amount = forms.DecimalField()

    class Meta:
        model = Sale
        fields = ['fruit', 'quantity', 'total_amount', 'sale_date']

    def clean(self) -> Dict[str, Union[str, int, float]]:
        cleaned_data = super().clean()
        fruit = cleaned_data.get('fruit')
        quantity = cleaned_data.get('quantity')

        if not Fruit.objects.filter(name=fruit).exists():
            raise forms.ValidationError('Selected fruit does not exist.')

        if 'total_amount' in cleaned_data:
            current_price = fruit.price
            total_amount = quantity * current_price
            if cleaned_data.get('total_amount') != total_amount:
                raise forms.ValidationError(
                    'Total amount does not match the current price.')

        return cleaned_data

class BulkSaleForm(forms.Form):
    csv_file = forms.FileField()

class SaleEditForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['fruit', 'quantity', 'sale_date']

    def clean(self) -> Dict[str, Any]:
        cleaned_data = super().clean()
        fruit = cleaned_data.get('fruit')
        quantity = cleaned_data.get('quantity')

        if not Fruit.objects.filter(name=fruit).exists():
            raise forms.ValidationError('Selected fruit does not exist.')

        if 'total_amount' in cleaned_data:
            current_price = fruit.price
            total_amount = quantity * current_price
            if cleaned_data.get('total_amount') != total_amount:
                raise forms.ValidationError('Total amount does not match the current price.')

        return cleaned_data
