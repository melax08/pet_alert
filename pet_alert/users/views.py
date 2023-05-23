from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django_registration import signals
from django_registration.backends.activation.views import RegistrationView

from .forms import CreationForm, CreationFormWithoutPassword
from ads.forms import LostForm, FoundForm



# class SignUp(CreateView):
#     form_class = CreationForm
#     success_url = reverse_lazy('users:confirmation_info')
#     template_name = 'users/signup.html'

# def signup(request):
#     template = 'users/signup.html'
#     form = CreationForm(request.POST or None)
#     if form.is_valid():
#         temp = form.save(commit=False)
#         temp.active = False
#
#
# class ConfirmationInfo(TemplateView):
#     template_name = 'users/confirmation_info.html'
