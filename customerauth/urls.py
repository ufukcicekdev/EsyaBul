from django.urls import path, include
from customerauth import views
from django.conf.urls import handler404, handler500

app_name = "customerauth"

urlpatterns = [
    ## customer page ##
    #path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    path("dashboard/", views.customer_dashboard, name="dashboard"),
    ## address page ##
    path('dashboard/addresses/', views.address_list, name='address-list'),
    path('dashboard/delete_address/<int:address_id>/', views.delete_address, name='delete-address'),
    path('dashboard/edit_address/<int:address_id>/', views.edit_address, name='edit-address'),
    path('dashboard/create_address/', views.create_address, name='create-address'),
    path('get-subregions/', views.get_subregions, name='get_subregions'),

    path('dashboard/password/', views.password_change, name='password-process'),
    path('dashboard/notifications/', views.notifications, name='notifications'),
    path('dashboard/profile/', views.profile_update, name='profile'),
    path('dashboard/change-email/', views.change_email_view, name='change_email'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    ##MY STYLE##
    path('room-type/', views.room_type_selected, name='room-type'),
    path('home-type/', views.home_type_selected, name='home-type'),
    path('home-model/', views.home_model_selected, name='home-model'),
    path('space-definations/', views.space_definations_selected, name='space-definations'),
    path('time-range/', views.time_range_selected, name='time-range'),

    ##FORGET PASSWORD##
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),
    
    ## wishlist page ##
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("add-to-wishlist/", views.add_to_wishlist, name="add-to-wishlist"),
    path("remove-from-wishlist/", views.remove_wishlist, name="remove-from-wishlist"),


    #orders#
    path('dashboard/orders/', views.orders_List, name='orders-list'),
    path('dashboard/orders-detail/<str:order_number>/', views.orders_detail, name='orders-detail'),

    path('', include('main.urls')),


    path('signup/', views.register_view, name='sign-up'),
    path('accounts/confirm-email/<str:uidb64>/<str:token>/', views.confirm_email, name='account_confirm_email'),
]
