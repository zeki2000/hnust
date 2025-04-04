from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core import views as core_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/login/', core_views.login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', core_views.password_reset_view, name='password_reset'),
    path('accounts/send_verification_code/', core_views.send_verification_code, name='send_verification_code'),
    path('accounts/password_reset/confirm/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('user/dashboard/', core_views.user_dashboard, name='user_dashboard'),
    path('provider/dashboard/', core_views.provider_dashboard, name='provider_dashboard'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
