from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer


@swagger_auto_schema(
    method="post",
    operation_summary="Register a new user",
    operation_description="Creates a new user with an email, password, and role. If the role is not provided, it defaults to 'customer'. Returns the created user details.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],  # Required fields
        properties={
            "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="First name of the user"),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="Last name of the user"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description="User email"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD, description="User password"),
            "role": openapi.Schema(type=openapi.TYPE_STRING, description="Role of the user (Defaults to 'customer')", default="customer"),
        }
    ),
    responses={
        201: openapi.Response("User created successfully", UserSerializer),
        400: "Bad Request - Invalid data",
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    operation_summary="Login user and get JWT tokens",
    operation_description="Authenticates a user and returns access & refresh tokens.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["email", "password"],
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING, format="email", description="User email"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", description="User password"),
        },
    ),
    responses={
        200: openapi.Response(
            "Login successful",
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                    "access": openapi.Schema(type=openapi.TYPE_STRING, description="Access token"),
                },
            ),
        ),
        401: "Unauthorized - Invalid credentials",
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=email, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response(
            {"refresh": str(refresh), "access": str(refresh.access_token)}
        )
    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method="get",
    operation_summary="Get logged-in user profile",
    operation_description="Returns the profile details of the authenticated user.\n\n"
                          "🔹 **Authorization Required**: Use the format `Bearer <your_token>` in the header.",
    manual_parameters=[
        openapi.Parameter(
            "Authorization",
            openapi.IN_HEADER,
            description="**Format**: Bearer <your_token>",  # Explicit format
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={200: UserSerializer, 401: "Unauthorized"},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


def ping_pong(request):
    return JsonResponse({"message": "pong"})
