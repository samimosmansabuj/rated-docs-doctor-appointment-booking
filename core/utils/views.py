from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from django.db import transaction
import json

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
    
    def serializer_error_response(self, serializer=None, error=None) -> Response:
        if serializer and serializer.errors:
            detail = {
                key: str(value[0]) if isinstance(value, list) else str(value)
                for key, value in serializer.errors.items()
            }
        elif error:
            detail = error.detail if hasattr(error, "detail") else str(error)
        else:
            detail = "Validation error."
        return Response(
            {
                "success": False,
                "detail": detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def post(self, request, *args, **kwargs) -> Response:
        try:
            if self.get_serializer(data=request.data):
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                return self.success_response(serializer)
            return self.success_response()
        except ValidationError as e:
            return self.serializer_error_response(
                serializer=locals().get("serializer"),
                error=e
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )


class BaseCreateAPIView(CreateAPIView):
    success_message = "Created successfully"
    
    def success_response(self, serializer) -> Response:
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "success": True,
                "message": self.success_message
            }, status=status.HTTP_201_CREATED, headers=headers
        )

    def serializer_error_response(self, serializer=None, error=None) -> Response:
        if serializer and serializer.errors:
            detail = {
                key: str(value[0]) if isinstance(value, list) else str(value)
                for key, value in serializer.errors.items()
            }
        elif error:
            detail = error.detail if hasattr(error, "detail") else str(error)
        else:
            detail = "Validation error."
        return Response(
            {
                "success": False,
                "detail": detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def create(self, request, *args, **kwargs):
        print("data: ", request.data)
        # {'name': 'John', 'age': 25}

        print("body: ", request.body.decode("utf-8"))
        # b'{"name":"John","age":25}'
        
        body = json.loads(request.body)
        print(body)
        print("body: ", request.POST)
        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                return self.success_response(serializer)
        except ValidationError as e:
            return self.serializer_error_response(
                serializer=locals().get("serializer"),
                error=e
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "detail": str(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )
    


