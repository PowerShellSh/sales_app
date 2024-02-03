from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import (
    FruitListView,
    EditFruitView,
    DeleteFruitView,
    AddFruitView,
    SaleCombinedView,
    AddSaleView,
    EditSaleView,
    DeleteSaleView,
    SalesAggregateView,
)


urlpatterns = [
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    path('fruit/', FruitListView.as_view(), name='fruit'),
    path('fruit/<int:pk>/edit_fruit/',
         EditFruitView.as_view(), name='edit_fruit'),
    path('fruit/add_fruit/', AddFruitView.as_view(), name='add_fruit'),
    path('fruit/<int:pk>/delete/', DeleteFruitView.as_view(), name='delete_fruit'),
    path('sales_combined/', SaleCombinedView.as_view(), name='sales_combined'),
    path('add_sales/', AddSaleView.as_view(), name='add_sales'),
    path('edit_sales/<int:pk>/', EditSaleView.as_view(), name='edit_sales'),
    path('delete_sale/<int:pk>/', DeleteSaleView.as_view(), name='delete_sale'),
    path('sales_aggregate/', SalesAggregateView.as_view(), name='sales_aggregate'),
]
