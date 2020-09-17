from django.urls import path, re_path, include

app_name = 'api'

urlpatterns = [
    re_path(r'^users/', include('users.urls')),
    re_path(r'^cloud/', include('cloud.urls')),
]
