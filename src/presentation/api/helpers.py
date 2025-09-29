from fastapi import Request, HTTPException


def get_client_ip(request: Request) -> str:
    """
    Get the client IP address from the request.
    :param request: FastAPI request object.
    :raises HTTPException: 422 if no client information.
    """
    client = request.client
    if client is None:
        raise HTTPException(status_code=422, detail="No client information")
    return client.host
