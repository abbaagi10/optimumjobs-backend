# apps/users/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/v1/register/
    Inscription d'un nouvel utilisateur.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """
    GET /api/v1/profile/
    Récupère le profil de l'utilisateur connecté.

    PATCH /api/v1/profile/
    Met à jour partiellement le profil de l'utilisateur connecté.
    
    Accessible à tous les utilisateurs authentifiés (candidats, organisations, admins).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Récupère le profil de l'utilisateur connecté.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """
        Met à jour partiellement le profil de l'utilisateur connecté.
        """
        # Champs que l'utilisateur peut modifier
        allowed_fields = ['first_name', 'last_name', 'phone', 'city', 'country', 'bio']
        
        # Filtrer les données pour ne garder que les champs autorisés
        filtered_data = {}
        for field in allowed_fields:
            if field in request.data:
                filtered_data[field] = request.data[field]

        # Si aucun champ autorisé n'est fourni
        if not filtered_data:
            return Response(
                {"detail": "Aucun champ valide à mettre à jour."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Sérialiser et valider les données
        serializer = UserSerializer(
            request.user,
            data=filtered_data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)