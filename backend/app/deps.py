from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.clerk_auth import verify_clerk_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    claims = verify_clerk_token(token)

    clerk_id = claims.get("sub")
    email = claims.get("email") or claims.get("email_address")
    name = claims.get("name") or email or "Unknown"
    role = (claims.get("public_metadata") or {}).get("role", "student")

    if not clerk_id:
        raise HTTPException(status_code=401, detail="Invalid token claims")

    user = db.query(User).filter(User.clerk_id == clerk_id).first()

    if user is None:
        # first login — upsert into our users table
        user = User(clerk_id=clerk_id, email=email, name=name, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # keep role in sync with Clerk metadata in case it changed
        if user.role != role:
            user.role = role
            db.commit()
            db.refresh(user)

    return user


def require_role(*allowed_roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker