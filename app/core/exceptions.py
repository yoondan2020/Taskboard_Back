# app/core/exceptions.py
"""
표준 예외 정의
앱 전체에서 일관된 에러 메시지를 사용하기 위한 모듈
"""
from fastapi import HTTPException, status


# ===== 404 Not Found =====
class NotFoundException(HTTPException):
    """리소스를 찾을 수 없을 때 사용하는 예외"""
    def __init__(self, resource_name: str, resource_id: int = None):
        detail = f"{resource_name} not found"
        if resource_id:
            detail = f"{resource_name} with id {resource_id} not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# ===== 400 Bad Request =====
class InvalidInputException(HTTPException):
    """입력값이 유효하지 않을 때 사용하는 예외"""
    def __init__(self, field_name: str, reason: str = None):
        detail = f"Invalid {field_name}"
        if reason:
            detail = f"Invalid {field_name}: {reason}"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


# ===== 403 Forbidden =====
class PermissionDeniedException(HTTPException):
    """권한이 없을 때 사용하는 예외"""
    def __init__(self, action: str = None):
        detail = "Permission denied"
        if action:
            detail = f"Permission denied: {action}"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ===== 409 Conflict =====
class ConflictException(HTTPException):
    """리소스 충돌이 발생했을 때 사용하는 예외"""
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


# ===== 편의 함수 =====
def project_not_found(project_id: int = None):
    """프로젝트를 찾을 수 없을 때"""
    return NotFoundException("Project", project_id)


def project_stage_not_found(project_stage_id: int = None):
    """프로젝트 단계를 찾을 수 없을 때"""
    return NotFoundException("Project stage", project_stage_id)


def user_not_found(user_id: int = None):
    """사용자를 찾을 수 없을 때"""
    return NotFoundException("User", user_id)


def state_not_found(state_id: int = None):
    """상태를 찾을 수 없을 때"""
    return NotFoundException("State", state_id)


def product_group_not_found(product_group_id: int = None):
    """제품군을 찾을 수 없을 때"""
    return NotFoundException("Product group", product_group_id)


def stage_not_found(stage_id: int = None):
    """단계를 찾을 수 없을 때"""
    return NotFoundException("Stage", stage_id)


def already_deleted():
    """이미 삭제된 리소스일 때"""
    return ConflictException("Resource already deleted")


def invalid_owner(reason: str = "Owner is not active"):
    """유효하지 않은 담당자일 때"""
    return InvalidInputException("owner_id", reason)
