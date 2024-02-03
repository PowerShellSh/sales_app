from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from .views import TopPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('top/', TopPageView.as_view(), name='top'),
    path('accounts/login/', LoginView.as_view(next_page='top'), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('sales/', include('sales.urls')),
    path('', LoginView.as_view(next_page='top'), name='login'),
]
