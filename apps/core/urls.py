from django.urls import path
from .views import api_root, home, login_view, register_view, dashboard_view

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login_page'),
    path('register/', register_view, name='register_page'),
    path('dashboard/', dashboard_view, name='dashboard_page'),
    path('api-root/', api_root, name='api-root'),
]
