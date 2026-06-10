from rest_framework.response import Response

def custom_response(success=True, message=None, detail=None, data=None, status=200):
    response = {
        "success": success,
    }
    if message is not None:
        response["message"] = message
    if detail is not None:
        response["detail"] = detail
    if data is not None:
        response["data"] = data
    return Response(
        response, status=status
    )


