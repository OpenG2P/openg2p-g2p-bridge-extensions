from typing import Any

from openg2p_fastapi_common.service import BaseService

from ..models import NotificationType, Recipient


class NotificationInterface(BaseService):
    def send_notification(
        self,
        notification_id: str,
        payload: Any,
        notification_type: NotificationType,
        recipient: Recipient,
    ) -> None:
        """
        Send a notification to a list of recipients.
        """
        pass
