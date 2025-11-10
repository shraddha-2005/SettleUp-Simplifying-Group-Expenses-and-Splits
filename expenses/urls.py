from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='home'),  
    path('dashboard/', views.dashboard, name='dashboard'),  
    path('create-group/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/add-expense/', views.add_expense, name='add_expense'),
    path('group/<int:group_id>/settlement/', views.settlement, name='settlement'),
    path('group/<int:group_id>/participant/<int:participant_id>/delete/', views.delete_participant, name='delete_participant'),
    path('group/<int:group_id>/delete/', views.delete_group, name='delete_group'),
]