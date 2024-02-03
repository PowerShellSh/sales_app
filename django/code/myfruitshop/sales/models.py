from django.db import models

class Fruit(models.Model):
    name: str = models.CharField(max_length=255)
    price: int = models.PositiveIntegerField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    is_active: bool = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

class Sale(models.Model):
    fruit: models.ForeignKey = models.ForeignKey(Fruit, on_delete=models.CASCADE)
    quantity: int = models.PositiveIntegerField()
    total_amount: int = models.PositiveIntegerField()
    sale_date: models.DateTimeField = models.DateTimeField()
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    is_active: bool = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.fruit.name} - {self.quantity} units - {self.sale_date}"
