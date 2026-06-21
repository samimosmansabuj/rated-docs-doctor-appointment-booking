from rest_framework import viewsets
from .models import Procedure
from .serializers import ProcedureSerializer, SubProcedureSerializer
from .permissions import IsAdminOrReadOnly
from .utils.viewsets import OwnModelViewSet
from .constants import PROCEDURE_CHOICES


class ProcedureViewSet(OwnModelViewSet):
    queryset = Procedure.objects.filter(type=PROCEDURE_CHOICES.OBJECTTIVE)[:10]
    serializer_class = SubProcedureSerializer
    permission_classes = [IsAdminOrReadOnly]


class MainProcedureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Procedure.objects.filter(type=PROCEDURE_CHOICES.MAIN)
    serializer_class = ProcedureSerializer
    permission_classes = [IsAdminOrReadOnly]




