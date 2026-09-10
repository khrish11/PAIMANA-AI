"""RBAC security helpers.

Demo implementation uses X-User-Role header.
Structured for drop-in JWT replacement in production.
"""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Any

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel


if TYPE_CHECKING:
    from typing import Self


class Role(IntEnum):
    """Role hierarchy — higher ordinal = more privileges."""
    VIEWER = 0
    AGENCY = 1
    ANALYST = 2
    REVIEWER = 3
    ADMIN = 4


ROLE_MAP = {
    "viewer": Role.VIEWER,
    "agency": Role.AGENCY,
    "analyst": Role.ANALYST,
    "reviewer": Role.REVIEWER,
    "admin": Role.ADMIN,
}


class CurrentUser(BaseModel):
    username: str
    role: Role
    role_name: str
    agency: str | None = None


def get_current_user(
    x_user_role: str | None = Header(default=None),
    x_username: str | None = Header(default=None),
    x_user_agency: str | None = Header(default=None),
) -> dict:
    """Extract user context from headers (demo mode).

    In production, replace with JWT token validation.
    """
    if not x_user_role or not x_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Send X-User-Role and X-Username headers.",
        )

    role_name = x_user_role.lower().strip()
    role = ROLE_MAP.get(role_name)
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role '{x_user_role}'. Valid roles: {list(ROLE_MAP.keys())}",
        )
    return {
        "username": x_username,
        "role": role,
        "role_name": role_name,
        "agency": x_user_agency,
    }


class RequireRole:
    """Dependency class that enforces exact minimum role level."""
    
    def __init__(self, min_role: Role):
        self.min_role = min_role
    
    def __call__(self, user = Depends(get_current_user)):
        # Only allow users with exactly the minimum role or higher for specific operations
        # For project creation, only AGENCY should be allowed
        if user["role"] != self.min_role:
            # For operations that require specific roles (not hierarchical)
            # Check if this is a role-specific operation
            if self.min_role == Role.AGENCY:
                # Only AGENCY can create projects
                if user["role"] != Role.AGENCY:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient privileges. Required: {self.min_role.name}, Current: {user['role_name']}."
                    )
            elif user["role"] < self.min_role:
                # For hierarchical operations, check minimum level
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Insufficient privileges. Required: {self.min_role.name}, "
                        f"Current: {user['role_name']}."
                    ),
                )
        return user


def require_role(min_role: Role):
    """Dependency that enforces minimum role level."""
    return RequireRole(min_role)
