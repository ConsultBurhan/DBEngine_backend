"""Permission service for managing role-based permissions."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from models.service_models.permission.permission_service_models import (
    PermissionList,
    SavePermissions,
)
from models.common import ResponseData, UResponse
from config.logger_config import get_logger

logger = get_logger(__name__)


class PermissionService:
    """Service for permission operations including saving and retrieving role permissions."""

    def __init__(
        self,
        user_id: int = 0,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self._user_id = user_id
        self._db_manager = db_manager or get_postgres_manager()

    async def save_permission_by_role_async(
        self, permission_dto: SavePermissions
    ) -> UResponse:
        """
        Save permissions for a role.
        Removes existing permissions and creates new ones from the DTO.
        """
        response = UResponse(
            Status=0,
            Message="Permissions saved successfully"
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Fetch existing permissions for the role
                select_query = text("""
                    SELECT id FROM permission
                    WHERE roleid = :role_id
                """)
                result = await session.execute(
                    select_query, {"role_id": permission_dto.RoleId}
                )
                existing_permissions = result.mappings().all()

                # Remove existing permissions (hard delete)
                if existing_permissions:
                    delete_query = text("""
                        DELETE FROM permission
                        WHERE roleid = :role_id
                    """)
                    await session.execute(delete_query, {"role_id": permission_dto.RoleId})

                # Create new permissions from the DTO
                # Only add permissions where at least one flag is true
                now = datetime.now()
                new_permissions = [
                    p for p in permission_dto.Permissions
                    if p.CanView or p.CanCreate or p.CanUpdate or p.CanDelete
                ]

                for p in new_permissions:
                    insert_query = text("""
                        INSERT INTO permission (
                            roleid, permissiontaskid, canview, cancreate,
                            canupdate, candelete, createddate, isactive, createdby
                        ) VALUES (
                            :role_id, :permission_task_id, :can_view, :can_create,
                            :can_update, :can_delete, :created_date, :is_active, :created_by
                        )
                    """)
                    await session.execute(
                        insert_query,
                        {
                            "role_id": permission_dto.RoleId,
                            "permission_task_id": p.PermissionTaskId,
                            "can_view": p.CanView,
                            "can_create": p.CanCreate,
                            "can_update": p.CanUpdate,
                            "can_delete": p.CanDelete,
                            "created_date": now,
                            "is_active": True,
                            "created_by": str(self._user_id) if self._user_id else None,
                        },
                    )

                await session.commit()

                response.Status = 0
                response.Message = f"Bulk permissions saved successfully for role {permission_dto.RoleId}"

        except Exception as ex:
            logger.error(f"Error saving permissions for role {permission_dto.RoleId}: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while saving permissions: {str(ex)}"

        return response

    async def get_permissions_list_async(
        self, role_id: int
    ) -> ResponseData[List[PermissionList]]:
        """
        Get permission list for a role with permission flags.
        """
        result = ResponseData[List[PermissionList]](
            Success=True,
            Message="SUCCESS",
            Data=[],
        )

        try:
            async with await self._db_manager.get_session() as session:
                # Fetch all active permission tasks
                tasks_query = text("""
                    SELECT id, permissiontaskname, parentid, displayorder, icon
                    FROM permissiontasks
                    WHERE isactive = TRUE
                    ORDER BY displayorder, permissiontaskname
                """)
                tasks_result = await session.execute(tasks_query)
                all_permission_tasks = tasks_result.mappings().all()

                # Fetch existing permissions for this role
                perms_query = text("""
                    SELECT id, permissiontaskid, canview, cancreate, canupdate, candelete
                    FROM permission
                    WHERE roleid = :role_id
                """)
                perms_result = await session.execute(perms_query, {"role_id": role_id})
                existing_permissions = perms_result.mappings().all()

                # Create a dictionary for quick lookup of existing permissions
                existing_perms_dict = {
                    p["permissiontaskid"]: p for p in existing_permissions
                }

                # Map permission tasks to DTOs with permission flags
                permission_list = []
                for pt in all_permission_tasks:
                    existing = existing_perms_dict.get(pt["id"], None)
                    if existing is None: continue
                    permission_list.append(
                        PermissionList(
                            PermissionTaskId=pt["id"],
                            PermissionTaskName=pt["permissiontaskname"],
                            ParentId=pt["parentid"],
                            DisplayOrder=pt["displayorder"],
                            Icon=pt["icon"],
                            CanView=existing["canview"] if existing and existing["canview"] else False,
                            CanCreate=existing["cancreate"] if existing and existing["cancreate"] else False,
                            CanUpdate=existing["canupdate"] if existing and existing["canupdate"] else False,
                            CanDelete=existing["candelete"] if existing and existing["candelete"] else False,
                            PermissionId=existing["id"] if existing else None,
                        )
                    )

                result.Data = permission_list

        except Exception as ex:
            logger.error(f"Error fetching permissions for role {role_id}: {ex}")
            result.Success = False
            result.Message = f"An error occurred while fetching permissions: {str(ex)}"
            result.Data = []

        return result
