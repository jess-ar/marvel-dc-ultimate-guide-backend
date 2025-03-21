from django.contrib.auth import authenticate, login
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .serializers import UserSerializer
from .models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                # Crear usuario
                user = serializer.save()
                email = user.email
                password = request.data.get('password')

                # Autenticar al usuario recién creado
                user = authenticate(username=email, password=password)

                if user and user.is_active:
                    login(request, user)

                    # Generar tokens
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)

                    # Respuesta al frontend
                    return Response({
                        'access': access_token,
                        'refresh': refresh_token,
                        'message': 'User registered successfully'
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Authentication failed. User may be inactive.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                # Errores de validación del serializer
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log para depurar errores inesperados
            print(f"Unknown error during registration: {str(e)}")
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Autenticar directamente por email (si tienes un backend de autenticación configurado para permitir autenticación por email)
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            user.delete()
            return Response({'detail': 'User successfully deleted'}, status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(status=status.HTTP_205_RESET_CONTENT)
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            print("Authorization header:", request.headers.get('Authorization'))
            print("User:", request.user)

            user = request.user
            if user.is_authenticated:
                return Response({
                    "username": user.username,
                    "email": user.email,
                    "avatar": user.avatar.url if user.avatar and hasattr(user.avatar, 'url') else None,
                })
            else:
                return Response({'error': 'User is not authenticated'}, status=401)

        except Exception as e:
            print(f"Error in UserMeView: {e}")
            return Response({'error': 'Internal Server Error'}, status=500)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        # Verificar que la contraseña antigua sea correcta
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect.'}, status=400)

        # Actualizar la contraseña
        if new_password:
            user.password = make_password(new_password)
            user.save()
            return Response({'message': 'Password updated successfully.'}, status=200)
        return Response({'error': 'New password is required.'}, status=400)