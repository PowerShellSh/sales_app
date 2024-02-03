from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpRequest, HttpResponse

class TopPageView(LoginRequiredMixin, View):
    template_name: str = 'top.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name)
