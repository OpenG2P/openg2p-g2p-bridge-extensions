from openg2p_fastapi_common.service import BaseService

from ..implementations.novu_notifier import NovuNotifier
from ..interface.notification_interface import NotificationInterface


class NotificationFactory(BaseService):
    @staticmethod
    def get_notifier() -> NotificationInterface:
        return NovuNotifier.get_component()
