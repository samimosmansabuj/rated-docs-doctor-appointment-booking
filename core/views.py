from rest_framework import viewsets
from .models import Procedure
from .serializers import ProcedureSerializer, SubProcedureSerializer
from .permissions import IsAdminOrReadOnly
from .utils.viewsets import OwnModelViewSet
from .constants import PROCEDURE_CHOICES
from rest_framework.response import Response
from rest_framework import status


class ProcedureViewSet(OwnModelViewSet):
    queryset = Procedure.objects.filter(type=PROCEDURE_CHOICES.OBJECTTIVE)
    serializer_class = SubProcedureSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())[:10]
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return self.list_success_response(serializer)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": str(e),
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MainProcedureViewSet(OwnModelViewSet):
    queryset = Procedure.objects.filter(type=PROCEDURE_CHOICES.MAIN)
    serializer_class = ProcedureSerializer
    permission_classes = [IsAdminOrReadOnly]




