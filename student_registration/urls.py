from django.contrib import admin
from django.urls import path, include
from home.views import landing, home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing, name='landing'),
    path('home/', home, name='home'),
    path('registration/', include('registration.urls')),
]