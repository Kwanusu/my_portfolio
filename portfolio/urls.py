from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessageReplyView, SystemLogViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView)

from rest_framework.authtoken import views
# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'communication/messages', MessageViewSet, basename='messages')
router.register(r'monitoring/logs', SystemLogViewSet, basename='logs')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # 1. SPECIFIC ROUTE FIRST
    path('api/v1/communication/messages/<int:pk>/reply/', MessageReplyView.as_view(), name='message-reply'),

    # 2. BROAD ROUTER SECOND
    path('api/v1/', include(router.urls)),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/login/', views.obtain_auth_token, name='api_token_auth'),
]