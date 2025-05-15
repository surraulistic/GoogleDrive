import logging

from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status
from starlette.responses import JSONResponse

from app.auth import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_prefix: str = "/files", excluded_routes: list[str] = None):
        super().__init__(app)
        self.protected_prefix = protected_prefix
        self.excluded_routes = set(excluded_routes) if excluded_routes else set()
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        logger.info(path)
        if path.startswith(self.protected_prefix) and path not in self.excluded_routes:
            token = request.headers.get("Authorization")
            logger.info(token)
            if not token or not token.startswith("Bearer "):
                return JSONResponse({"error": "Unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
            token = token.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                request.state.user = payload
            except JWTError:
                return JSONResponse({"error": "Invalid token"}, status_code=status.HTTP_403_FORBIDDEN)

        response = await call_next(request)
        return response