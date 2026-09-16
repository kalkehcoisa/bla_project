import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.notify_task_completed")
def notify_task_completed(task_id: int, task_title: str, assignee_email: str | None) -> str:
    """Simulates sending a notification when a task is marked as done.

    In a real system this would send an email or push notification.
    Kept simple here so it runs without external services during the demo.
    """
    message = f"Task #{task_id} '{task_title}' completed"
    if assignee_email:
        message += f", notifying {assignee_email}"
    logger.info(message)
    return message
