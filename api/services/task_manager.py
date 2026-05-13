from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from api.models import TaskDetail, TaskSummary


class TaskManager:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskDetail] = {}
        self._lock = Lock()

    def create_task(self, task_id: str, title: str, url: str) -> TaskDetail:
        task = TaskDetail(
            id=task_id,
            title=title,
            url=url,
            status="queued",
            progress=0,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._tasks[task_id] = task
        return task

    def update_task(self, task_id: str, **kwargs: object) -> TaskDetail:
        with self._lock:
            task = self._tasks[task_id]
            updated = task.model_copy(update=kwargs)
            self._tasks[task_id] = updated
            return updated

    def append_log(self, task_id: str, line: str) -> TaskDetail:
        with self._lock:
            task = self._tasks[task_id]
            updated = task.model_copy(update={"logs": [*task.logs, line]})
            self._tasks[task_id] = updated
            return updated

    def append_output_file(self, task_id: str, file_path: str) -> TaskDetail:
        with self._lock:
            task = self._tasks[task_id]
            updated = task.model_copy(
                update={"output_files": [*task.output_files, file_path]}
            )
            self._tasks[task_id] = updated
            return updated

    def get_task(self, task_id: str) -> TaskDetail:
        with self._lock:
            return self._tasks[task_id]

    def list_tasks(self) -> list[TaskSummary]:
        with self._lock:
            return [
                TaskSummary(
                    id=task.id,
                    title=task.title,
                    status=task.status,
                    progress=task.progress,
                    created_at=task.created_at,
                )
                for task in sorted(
                    self._tasks.values(),
                    key=lambda item: item.created_at,
                    reverse=True,
                )
            ]
