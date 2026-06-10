from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.exceptions import ValidationError

class OwnAPIView(APIView):
    serializer_class = None
    
    def get_serializer(self, data):
        if self.serializer_class:
            return self.serializer_class(data=data, context={"request": self.request})
        return None
    
    def success_response(self, serializer=None) -> Response:
        return Response(
            {
                "success": True,
                "detail": ""
            }, status=status.HTTP_200_OK
        )
    
    def serializer_error_response(self, serializer) -> Response:
        return Response(
            {
                "success": False,
                "detail": {key: str(value[0]) for key, value in serializer.errors.items()}
            }, status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request, *args, **kwargs) -> Response:
        try:
            if self.get_serializer(data=request.data):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                return self.success_response(serializer)
            else:
                return self.success_response()
        except ValidationError:
            return self.serializer_error_response(serializer)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )


