from django.urls import path, include
from customerauth import views
from django.conf.urls import handler404, handler500
from .views import custom_404_page, custom_500_page



app_name = "customerauth"

urlpatterns = [

    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    path("profile/update/", views.profile_update, name="profile-update"),
    path("dashboard/", views.customer_dashboard, name="dashboard"),
    # path("dashboard/adress", views.customer_address, name="cutomer-address"),
    # path("dashboard/adress/edit-address/<int:address_id>/", views.edit_address, name="edit_address"),


    path('dashboard/addresses/', views.address_list, name='address-list'),
    path('dashboard/edit_address/<int:address_id>/', views.edit_address, name='edit-address'),
    path('dashboard/delete_address/<int:address_id>/', views.delete_address, name='delete-address'),


    # path("make-default-address/", views.make_address_default, name="make-default-address"),
    # path("delete-adress/", views.delete_adress, name="delete-adress"),
    #path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),

    path('thank-you/', views.thank_you_view, name='thank_you'),


    ##MY STYLE##
    path('room-type/', views.room_type_selected, name='room-type'),
    path('home-type/', views.home_type_selected, name='home-type'),
    path('home-model/', views.home_model_selected, name='home-model'),
    path('space-definations/', views.space_definations_selected, name='space-definations'),
    path('time-range/', views.time_range_selected, name='time-range'),




    ##FORGET PASSWORD##
    path("forgot-password/",views.forgot_password, name="forgot_password"),
    path("reset-password/",views.reset_password,name="reset_password"),

    path('', include('main.urls')),
]


handler404 = custom_404_page
handler500 = custom_500_page
