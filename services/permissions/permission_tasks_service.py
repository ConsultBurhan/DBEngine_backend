"""Permission task service for managing permission tasks/privileges."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import text

from database.dbConnection.postgres_connection import (
    get_postgres_manager,
    PostgresConnectionManager,
)
from models.service_models.permission.permission_service_models import (
    PermissionTaskList,
    AddPermissionTask,
    UpdatePermissionTask,
)
from models.common import ResponseData, UResponse, UEntity
from config.logger_config import get_logger

logger = get_logger(__name__)


class PermissiontaskService:
    """Service for permission task operations including CRUD operations."""

    def __init__(
        self,
        db_manager: Optional[PostgresConnectionManager] = None,
    ):
        self._db_manager = db_manager or get_postgres_manager()

    async def get_all_permission_tasks_async(self) -> ResponseData[List[PermissionTaskList]]:
        """Get all active permission tasks ordered by display order and name."""
        result = ResponseData[List[PermissionTaskList]](
            Success=True,
            Message="SUCCESS",
            Data=[],
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT id, permissiontaskname, path, parentid, isactive,
                           displayorder, icon, createddate, createdby,
                           updateddate, updatedby
                    FROM permissiontasks
                    WHERE isactive = TRUE
                    ORDER BY displayorder, permissiontaskname
                """)
                query_result = await session.execute(query)
                permission_tasks = query_result.mappings().all()

                if not permission_tasks:
                    result.Data = []
                    return result

                # Map to DTO with parent permission task name
                permission_dtos = []
                for pt in permission_tasks:
                    parent_name = None
                    if pt["parentid"] is not None:
                        # Find parent name from the list
                        for parent in permission_tasks:
                            if parent["id"] == pt["parentid"]:
                                parent_name = parent["permissiontaskname"]
                                break

                    permission_dtos.append(
                        PermissionTaskList(
                            Id=pt["id"],
                            Permissiontaskname=pt["permissiontaskname"],
                            Path=pt["path"],
                            Parentid=pt["parentid"],
                            Isactive=pt["isactive"],
                            Displayorder=pt["displayorder"],
                            Icon=pt["icon"],
                            Createddate=pt["createddate"],
                            Createdby=pt["createdby"],
                            Updateddate=pt["updateddate"],
                            Updatedby=pt["updatedby"],
                            ParentPermissionTaskName=parent_name,
                        )
                    )

                result.Data = permission_dtos

        except Exception as ex:
            logger.error(f"Error fetching permission tasks: {ex}")
            result.Success = False
            result.Message = f"An error occurred while fetching permissions: {str(ex)}"
            result.Data = []

        return result

    async def get_permission_task_by_id_async(self, task_id: int) -> ResponseData[PermissionTaskList]:
        """Get a specific permission task by ID."""
        result = ResponseData[PermissionTaskList](
            Success=True,
            Message="SUCCESS",
            Data=None,
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT id, permissiontaskname, path, parentid, isactive,
                           displayorder, icon, createddate, createdby,
                           updateddate, updatedby
                    FROM permissiontasks
                    WHERE id = :task_id AND isactive = TRUE
                """)
                query_result = await session.execute(query, {"task_id": task_id})
                permission = query_result.mappings().first()

                if permission is None:
                    result.Success = False
                    result.Message = "No permission task found"
                    return result

                # Get parent permission task name if parentid is set
                parent_name = None
                if permission["parentid"] is not None:
                    parent_query = text("""
                        SELECT permissiontaskname
                        FROM permissiontasks
                        WHERE id = :parent_id
                    """)
                    parent_result = await session.execute(
                        parent_query, {"parent_id": permission["parentid"]}
                    )
                    parent_row = parent_result.mappings().first()
                    if parent_row:
                        parent_name = parent_row["permissiontaskname"]

                result.Data = PermissionTaskList(
                    Id=permission["id"],
                    Permissiontaskname=permission["permissiontaskname"],
                    Path=permission["path"],
                    Parentid=permission["parentid"],
                    Isactive=permission["isactive"],
                    Displayorder=permission["displayorder"],
                    Icon=permission["icon"],
                    Createddate=permission["createddate"],
                    Createdby=permission["createdby"],
                    Updateddate=permission["updateddate"],
                    Updatedby=permission["updatedby"],
                    ParentPermissionTaskName=parent_name,
                )

        except Exception as ex:
            logger.error(f"Error fetching permission task by ID: {ex}")
            result.Success = False
            result.Message = f"An error occurred while fetching the permission task: {str(ex)}"

        return result

    async def create_permission_task_async(
        self, permission_task_dto: AddPermissionTask
    ) -> UResponse:
        """Create a new permission task."""
        response = UResponse(Status=0, Message="")

        try:
            # Validate permission task name
            if not permission_task_dto.Permissiontaskname or not permission_task_dto.Permissiontaskname.strip():
                response.Status = 1
                response.Message = "Permission task name cannot be empty."
                return response

            async with await self._db_manager.get_session() as session:
                # Check for existing permission with same name
                check_query = text("""
                    SELECT id FROM permissiontasks
                    WHERE LOWER(permissiontaskname) = LOWER(:name)
                """)
                check_result = await session.execute(
                    check_query,
                    {"name": permission_task_dto.Permissiontaskname.strip()},
                )
                existing = check_result.mappings().first()

                if existing:
                    response.Status = 1
                    response.Message = "A permission task with this name already exists."
                    return response

                # Insert new permission task
                now = datetime.now()
                insert_query = text("""
                    INSERT INTO permissiontasks (
                        permissiontaskname, path, parentid, displayorder,
                        icon, isactive, createdby, createddate
                    ) VALUES (
                        :name, :path, :parentid, :displayorder,
                        :icon, :isactive, :createdby, :createddate
                    )
                """)
                await session.execute(
                    insert_query,
                    {
                        "name": permission_task_dto.Permissiontaskname.strip(),
                        "path": permission_task_dto.Path,
                        "parentid": permission_task_dto.Parentid,
                        "displayorder": permission_task_dto.Displayorder,
                        "icon": permission_task_dto.Icon,
                        "isactive": permission_task_dto.Isactive,
                        "createdby": permission_task_dto.Createdby,
                        "createddate": now,
                    },
                )
                await session.commit()

                response.Status = 0
                response.Message = "Permission task created successfully"

        except Exception as ex:
            logger.error(f"Error creating permission task: {ex}")
            response.Status = 1
            response.Message = f"An error occurred while creating the permission task: {str(ex)}"

        return response

    async def update_permission_task_async(
        self, permission_task_dto: UpdatePermissionTask
    ) -> UResponse:
        """Update an existing permission task."""
        result = UResponse(Status=0, Message="")

        try:
            # Validate permission task name
            if not permission_task_dto.Permissiontaskname or not permission_task_dto.Permissiontaskname.strip():
                result.Status = 1
                result.Message = "Permission task name cannot be empty."
                return result

            async with await self._db_manager.get_session() as session:
                # Check if permission task exists
                check_exists_query = text("""
                    SELECT id FROM permissiontasks WHERE id = :task_id
                """)
                check_result = await session.execute(
                    check_exists_query, {"task_id": permission_task_dto.Id}
                )
                existing_task = check_result.mappings().first()

                if not existing_task:
                    result.Status = 1
                    result.Message = "No permission task found with the provided ID."
                    return result

                # Check for duplicate name (excluding current task)
                duplicate_check_query = text("""
                    SELECT id FROM permissiontasks
                    WHERE LOWER(permissiontaskname) = LOWER(:name)
                    AND id != :task_id
                """)
                duplicate_result = await session.execute(
                    duplicate_check_query,
                    {
                        "name": permission_task_dto.Permissiontaskname.strip(),
                        "task_id": permission_task_dto.Id,
                    },
                )
                duplicate = duplicate_result.mappings().first()

                if duplicate:
                    result.Status = 1
                    result.Message = "Another permission task with the same name already exists."
                    return result

                # Update permission task
                now = datetime.now()
                update_query = text("""
                    UPDATE permissiontasks
                    SET permissiontaskname = :name,
                        path = :path,
                        parentid = :parentid,
                        isactive = :isactive,
                        displayorder = :displayorder,
                        icon = :icon,
                        updateddate = :updateddate,
                        updatedby = :updatedby
                    WHERE id = :task_id
                """)
                await session.execute(
                    update_query,
                    {
                        "name": permission_task_dto.Permissiontaskname,
                        "path": permission_task_dto.Path,
                        "parentid": permission_task_dto.Parentid,
                        "isactive": permission_task_dto.Isactive,
                        "displayorder": permission_task_dto.Displayorder,
                        "icon": permission_task_dto.Icon,
                        "updateddate": now,
                        "updatedby": permission_task_dto.Updatedby,
                        "task_id": permission_task_dto.Id,
                    },
                )
                await session.commit()

                result.Status = 0
                result.Message = "Permission task updated successfully"

        except Exception as ex:
            logger.error(f"Error updating permission task: {ex}")
            result.Status = 1
            result.Message = f"An error occurred while updating permission task: {str(ex)}"

        return result

    async def delete_permission_task_async(self, task_id: int) -> UResponse:
        """Soft delete a permission task and its related permissions."""
        result = UResponse(Status=0, Message="")

        try:
            async with await self._db_manager.get_session() as session:
                # Check if permission task exists and is active
                check_query = text("""
                    SELECT id FROM permissiontasks
                    WHERE id = :task_id AND isactive = TRUE
                """)
                check_result = await session.execute(check_query, {"task_id": task_id})
                permission_task = check_result.mappings().first()

                if not permission_task:
                    result.Status = 1
                    result.Message = f"No active permission task found with ID {task_id}"
                    return result

                now = datetime.now()

                # Soft delete permission task
                update_task_query = text("""
                    UPDATE permissiontasks
                    SET isactive = FALSE, updateddate = :updateddate
                    WHERE id = :task_id
                """)
                await session.execute(
                    update_task_query,
                    {"task_id": task_id, "updateddate": now},
                )

                # Soft delete related permissions
                update_permissions_query = text("""
                    UPDATE permission
                    SET isactive = FALSE, updateddate = :updateddate
                    WHERE permissiontaskid = :task_id AND isactive = TRUE
                """)
                await session.execute(
                    update_permissions_query,
                    {"task_id": task_id, "updateddate": now},
                )

                await session.commit()

                result.Status = 0
                result.Message = "Permission task and related permissions deleted successfully (soft delete)"

        except Exception as ex:
            logger.error(f"Error deleting permission task: {ex}")
            result.Status = 1
            result.Message = f"Error occurred while deleting permission task: {str(ex)}"

        return result

    async def get_permission_tasks_dropdown_async(self) -> ResponseData[List[UEntity]]:
        """Get permission tasks for dropdown (Id and Name only)."""
        result = ResponseData[List[UEntity]](
            Success=True,
            Message="SUCCESS",
            Data=[],
        )

        try:
            async with await self._db_manager.get_session() as session:
                query = text("""
                    SELECT id, permissiontaskname
                    FROM permissiontasks
                    WHERE isactive = TRUE
                    ORDER BY displayorder, permissiontaskname
                """)
                query_result = await session.execute(query)
                permission_tasks = query_result.mappings().all()

                if not permission_tasks:
                    result.Success = False
                    result.Message = "No permission tasks found"
                    return result

                # Map to UEntity
                permission_dtos = [
                    UEntity(Id=pt["id"], Name=pt["permissiontaskname"])
                    for pt in permission_tasks
                ]

                result.Data = permission_dtos

        except Exception as ex:
            logger.error(f"Error fetching permission tasks for dropdown: {ex}")
            result.Success = False
            result.Message = f"An error occurred while fetching permissions: {str(ex)}"
            result.Data = []

        return result
