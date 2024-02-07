from django.urls import path, include
from customerauth import views
from django.conf.urls import handler404, handler500

app_name = "customerauth"

urlpatterns = [

    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    #path("profile/update/", views.profile_update, name="profile-update"),
    path("dashboard/", views.customer_dashboard, name="dashboard"),
    # path("dashboard/adress", views.customer_address, name="cutomer-address"),
    # path("dashboard/adress/edit-address/<int:address_id>/", views.edit_address, name="edit_address"),


    path('dashboard/addresses/', views.address_list, name='address-list'),
    path('dashboard/edit_address/<int:address_id>/', views.edit_address, name='edit-address'),
    path('dashboard/delete_address/<int:address_id>/', views.delete_address, name='delete-address'),
    path('dashboard/create_address/', views.create_address, name='create-address'),

    path('dashboard/password/', views.password_change, name='password-process'),
    path('dashboard/notifications/', views.notifications, name='notifications'),
    path('dashboard/profile/', views.profile_update, name='profile'),



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


    ## wishlist page ##
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("add-to-wishlist/", views.add_to_wishlist, name="add-to-wishlist"),
    path("remove-from-wishlist/", views.remove_wishlist, name="remove-from-wishlist"),

    path('', include('main.urls')),
]
