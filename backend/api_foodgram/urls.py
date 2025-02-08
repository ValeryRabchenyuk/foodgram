from django.contrib import admin
from django.urls import include, path

from api.views import short_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<slug:short_link>/', short_url, name='short_url')]
