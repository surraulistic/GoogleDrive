from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from starlette.responses import JSONResponse

from config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefix: str = "/files", excluded_routes: list[str] = None):
        super().__init__(app)
        self.protected_prefix = protected_prefix
        self.excluded_routes = set(excluded_routes) if excluded_routes else set()
        self.secret_key = settings.auth_config.secret_key
        self.algorithm = settings.auth_config.algorithm
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith(self.protected_prefix) and not any(path.startswith(r) for r in self.excluded_routes):
            token = request.headers.get("Authorization")
            if not token or not token.startswith("Bearer "):
                return JSONResponse({"error": "Unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
            token = token.split(" ")[1]
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                request.state.user = payload
            except JWTError:
                return JSONResponse({"error": "Invalid token"}, status_code=status.HTTP_403_FORBIDDEN)
        response = await call_next(request)
        return response