"""
JWT Verification Middleware
Validates JWT tokens and extracts user_id for all protected routes
"""

from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from config import BETTER_AUTH_SECRET, JWT_ALGORITHM


async def verify_jwt_middleware(request: Request):
    """
    Middleware to verify JWT token and extract user_id

    This middleware:
    1. Extracts JWT token from Authorization header
    2. Verifies and decodes the token
    3. Extracts user_id from token payload
    4. Attaches user_id to request.state for use in route handlers

    Returns 401 Unauthorized if:
    - No Authorization header provided
    - Invalid token format
    - Token is expired or invalid
    """
    # Skip verification for auth endpoints (signup/signin)
    if request.url.path in ["/auth/signup", "/auth/signin"]:
        return

    # Skip for health check (if you add one)
    if request.url.path == "/health":
        return

    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    # Check for Bearer token format
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
        )

    # Extract token
    token = auth_header.split(" ")[1]

    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[JWT_ALGORITHM])

        # Extract user_id from payload
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id not found",
            )

        # Attach user_id to request state for route handlers
        request.state.user_id = user_id

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired JWT token: {str(e)}",
        )


def verify_user_id_match(request: Request, url_user_id: str) -> None:
    """
    Verify that user_id from JWT token matches user_id in URL path

    This is called in route handlers to enforce multi-user isolation per constitution

    Args:
        request: FastAPI request object with JWT-verified user_id in state
        url_user_id: user_id extracted from URL path parameter

    Raises:
        HTTPException: 401 Unauthorized if user_ids don't match
    """
    token_user_id = request.state.user_id

    if token_user_id != url_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: user_id mismatch. You can only access your own resources.",
        )
