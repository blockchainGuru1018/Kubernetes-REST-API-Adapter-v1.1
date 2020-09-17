from django.urls import path
from .views import SubscriptionCreateView, SubscriptionDeleteView, SubscriptionDetailView, \
    ControlServerView, ChangeServerView, GetBrokenSubscriptionsView, UpdateServiceDetail, Initialized
app_name = 'cloud'
from . import views

urlpatterns = [
    path('byp/setapprovedsubscriptions/', SubscriptionCreateView.as_view()),
    path('byp/getapprovedsubscriptions/<int:pk>/', SubscriptionDetailView.as_view()),
    path('byp/deleteapprovedsubscriptions/<int:pk>/', SubscriptionDeleteView.as_view()),
    path('byp/control_server/', ControlServerView.as_view()),
    path('tasks/', views.tasks, name='tasks'),
    path('byp/initialized/', Initialized.as_view()),

    path('byp.karel.cloud/byp/updateservicedetail/', UpdateServiceDetail.as_view()),
    path('byp.karel.cloud/byp/updateserverstate/', ChangeServerView.as_view()),
    path('byp.karel.cloud/byp/getbrokensubscriptions/', GetBrokenSubscriptionsView.as_view()),
]
