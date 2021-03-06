from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.views.generic import (
                    DetailView,
                    ListView,
                    UpdateView,
                    DeleteView,
                    CreateView
                )

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Tweet, TweetMedia
from .forms import TweetModelForm
from .mixins import OwnUserMixin

# Create your views here.

class RetweetView(View):
    def get(self, request, pk, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=pk)
        if request.user.is_authenticated():
            new_tweet = Tweet.objects.retweet(request.user, tweet)
            return HttpResponseRedirect("/")
        return HttpResponseRedirect(tweet.get_absolute_url())

# Create
class TweetCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    login_url = "/admin/"
    form_class = TweetModelForm
    template_name = "tweets/create_view.html"
    success_message = "Tweet was created successfully"
#    success_url = '/tweet'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(TweetCreateView, self).form_valid(form)

# Retrieve
class TweetDetailView(DetailView):
    queryset = Tweet.objects.all()
    template_name = "tweets/detail_view.html"

    # def get_object(self, queryset=queryset):
    #     return Tweet.objects.get(id=id)


class TweetListView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/list_view.html"

    def get_queryset(self, *args, **kwargs):
        qs = Tweet.objects.all()
        query = self.request.GET.get("q", None)
        if query is not None:
            qs = qs.filter(
                Q(content__icontains=query) |
                Q(user__username__icontains=query))
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super(TweetListView, self).get_context_data(*args, **kwargs)
        context['create_form'] = TweetModelForm()
        context['create_url'] = reverse_lazy("tweet:create")
        return context

# Update
class TweetUpdateView(SuccessMessageMixin, LoginRequiredMixin, OwnUserMixin, UpdateView):
#  model = Tweet # write the model or queryset
    queryset = Tweet.objects.all() #comment queryset and uncomment model
    login_url = "/admin/"
    form_class = TweetModelForm
    template_name = "tweets/update_view.html"
    success_message = "Tweet was updated successfully"
#    success_url = '/tweet'

# Delete

class TweetDeleteView(DeleteView):
    model = Tweet
    template_name = "tweets/delete_confirm.html"
    success_url = reverse_lazy("tweet:list")
