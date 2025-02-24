from django.http import  FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from attachments.models import Attachment
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer

User = get_user_model()

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

SERVICE_TYPES = [
    ("installation", "Installation"),
    ("maintenance", "Maintenance"),
    ("repair", "Repair"),
]

SERVICE_TYPE_CHOICES = [choice[0] for choice in SERVICE_TYPES]
@swagger_auto_schema(
    method='post',
    operation_summary="Create a service request with attachments",
    operation_description="Allows authenticated customers to create a service request with optional file attachments.\n\n"
                          "🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            name="attachments",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_FILE),
            description="Upload one or more attachment files",
            required=False,
            collection_format='multi'
        ),
        openapi.Parameter(
            name="title",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            description="Title of the service request",
            required=True,
        ),
        openapi.Parameter(
            name="description",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            description="Detailed description of the request",
            required=True,
        ),
        openapi.Parameter(
            name="service_type",
            in_=openapi.IN_FORM,
            type=openapi.TYPE_STRING,
            description="Type of service request (Select from: 'installation', 'maintenance', 'repair')",
            enum=SERVICE_TYPE_CHOICES,
            required=True,
        ),
    ],
    consumes=['multipart/form-data'],
    responses={
        201: openapi.Response(
            "Service request created",
            ServiceRequestSerializer
        ),
        400: openapi.Response("Bad Request - Invalid data"),
        401: openapi.Response("Unauthorized - Missing or invalid token"),
    },
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_service_request(request):
    user = request.user

    if user.role != "customer":
        return Response(
            {"detail": "Only customers can create service requests."},
            status=status.HTTP_403_FORBIDDEN
        )

    if 'service_type' not in request.data:
        return Response({"service_type": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

    serializer = ServiceRequestSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        service_request = serializer.save()
        return Response(ServiceRequestSerializer(service_request).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method="get",
    operation_summary="List service requests",
    operation_description="Fetch all service requests for the logged-in customer or assigned support staff with pagination\n\n"
                          "🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            description="Page number for pagination",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
    ],
    responses={
        200: openapi.Response("Service requests retrieved", ServiceRequestSerializer(many=True)),
        401: "Unauthorized",
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_requests(request):
    user = request.user
    if user.role == "support_staff":
        requests = ServiceRequest.objects.filter(support_staff=request.user)
    elif user.role == "customer":
        requests = ServiceRequest.objects.filter(customer=request.user)
    else:
        return Response({"detail": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

    paginator = CustomPagination()
    paginated_requests = paginator.paginate_queryset(requests, request)
    serializer = ServiceRequestSerializer(paginated_requests, many=True)
    return paginator.get_paginated_response(serializer.data)


@swagger_auto_schema(
    method="patch",
    operation_summary="Update service request status",
    operation_description="Allows support staff to update the status of a service request\n\n"
                          "🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["status"],
        properties={
            "status": openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=["pending", "in_progress", "resolved"],
                description="New status of the request"
            ),
        },
    ),
    responses={
        200: "Status updated successfully",
        400: "Invalid status value",
        404: "Request not found or unauthorized",
    },
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_service_request_status(request, request_id):
    try:
        service_request = ServiceRequest.objects.get(id=request_id, support_staff=request.user)
    except ServiceRequest.DoesNotExist:
        return Response({"detail": "Request not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    if new_status not in ["pending", "in_progress", "resolved"]:
        return Response({"detail": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

    service_request.status = new_status
    service_request.save()

    return Response({"detail": "Status updated successfully."})


@swagger_auto_schema(
    method="get",
    operation_summary="Get a service request",
    operation_description="Fetch a specific service request by ID (only if it belongs to the customer)\n\n"
                          "🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",  # Explicit format
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response("Service request retrieved", ServiceRequestSerializer),
        404: "Request not found",
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_service_request(request, request_id):
    try:
        service_request = ServiceRequest.objects.get(id=request_id, customer=request.user)
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data)
    except ServiceRequest.DoesNotExist:
        return Response({"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method="delete",
    operation_summary="Delete a service request",
    operation_description="Allows customers to delete their service request if it's still pending.\n\n"
                          "🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        204: "Request deleted successfully",
        400: "Cannot delete a request that is in progress or resolved",
        404: "Request not found",
    },
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_service_request(request, request_id):
    try:
        service_request = ServiceRequest.objects.get(id=request_id, customer=request.user)
    except ServiceRequest.DoesNotExist:
        return Response({"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

    if service_request.status != "pending":
        return Response(
            {"detail": "Cannot delete a request that is in progress or resolved."},
            status=status.HTTP_400_BAD_REQUEST
        )

    for attachment in service_request.attachments.all():
        attachment.delete()

    service_request.delete()
    return Response({"detail": "Request deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method="get",
    operation_summary="Download an attachment",
    operation_description="""
        Allows a customer or assigned support staff to download a file attachment. 
        The user must be either the customer who created the request or the assigned support staff\n\n
        🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.
    """,
    manual_parameters=[
openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "attachment_id",
            openapi.IN_PATH,
            description="The ID of the attachment to download",
            type=openapi.TYPE_INTEGER,
            required=True,
        )
    ],
    responses={
        200: "File download successful",
        403: "You do not have permission to download this file",
        404: "Attachment not found",
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_file(request, attachment_id):
    try:
        attachment = Attachment.objects.get(id=attachment_id)
        service_request = attachment.service_request
        if request.user != service_request.customer and request.user != service_request.support_staff:
            return Response({"error": "You do not have permission to download this file."}, status=status.HTTP_403_FORBIDDEN)

        file_path = attachment.file.path
        return FileResponse(open(file_path, "rb"), as_attachment=True)

    except Attachment.DoesNotExist:
        return Response({"error": "Attachment not found"}, status=status.HTTP_404_NOT_FOUND)
    except FileNotFoundError:
        raise Http404("File not found")
