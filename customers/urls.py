from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("maker/", views.maker_dashboard, name="maker_dashboard"),
    path(
        "maker/customers/new/",
        views.customer_create,
        name="customer_create",
    ),
    path(
        "maker/customers/<str:customer_id>/",
        views.maker_customer_detail,
        name="maker_customer_detail",
    ),

    path("checker/", views.checker_dashboard, name="checker_dashboard"),
    path(
        "checker/customers/<str:customer_id>/",
        views.checker_customer_detail,
        name="checker_customer_detail",
    ),
    path(
        "customers/<str:customer_id>/files/<str:file_type>/",
        views.customer_file,
        name="customer_file",
    ),
    path(
        "checker/customers/<str:customer_id>/review/",
        views.review_customer,
        name="review_customer",
    ),
    
    path(
        "admin-tools/clear-local-media/",
        views.clear_local_media,
        name="clear_local_media",
    ),
    
    path(
        "admin-tools/list-media/",
        views.list_local_media,
        name="list_local_media",
    ),
]
