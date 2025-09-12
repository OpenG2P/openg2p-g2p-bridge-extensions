# OpenG2P G2P Bridge Notification Module

This module provides a notification abstraction for the OpenG2P G2P Bridge, including:
- A NotificationInterface for sending notifications
- A Recipient model
- Reference implementations (e.g., Novu)

## Structure
- `src/openg2p_g2p_bridge_notification/interface/notification_interface.py`: Abstract interface for notification senders
- `src/openg2p_g2p_bridge_notification/models/recipient.py`: Recipient model
- `src/openg2p_g2p_bridge_notification/implementations/novu_notifier.py`: Novu reference implementation

## Usage
Import the interface and use a reference implementation to send notifications to recipients.
