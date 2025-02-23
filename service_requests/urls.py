from django.urls import path
from .views import (
    create_service_request,
    delete_service_request,
    update_service_request_status,
    list_requests,
)

urlpatterns = [
    path("service-request/create/", create_service_request, name="create_service_request"),
    path("service-request/getAll/", list_requests, name="get_all_service_request_by_staff"),
    path("service-request/delete/<int:request_id>/", delete_service_request, name="delete_service_request"),
    path("service-request/update/<int:request_id>/", update_service_request_status, name="update_service_request"),
]
