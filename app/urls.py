"""UrlPatterns for Yobota Case Study

Already provided,
"""
from django.conf.urls import url, include
from django.contrib import admin
#handler404 = 'connect4.templates.404'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^connect4/', include('connect4.urls')),

]
