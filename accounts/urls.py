from django.conf.urls import url

from .views import (
    UserDetailView,
    UserFollowView
    )

urlpatterns = [

     url(r'^(?P<username>[\w.@+-]+)/$', UserDetailView.as_view(), name='detail'),  # /profilename/
     url(r'^(?P<username>[\w.@+-]+)/follow/$', UserFollowView.as_view(), name='follow'),  # /profilename/

]
