from src.admin.services.admin_user_service import AdminUserService as RealAdminUserService

class AdminUserService(RealAdminUserService):
    """Bridge for AdminUserService in the shared services directory."""
    pass
