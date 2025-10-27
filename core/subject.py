from abc import ABC
from typing import Any


class Subject(ABC):
    """
    Defines the Subject class as an abstract base class for managing and notifying
    observers.

    The Subject class provides the structure for implementing the observer design
    pattern. It allows observers to attach or detach themselves and can notify
    these observers with a message.

    :ivar observers: A list to store the observers that are attached.
    :type observers: list
    """

    def attach(self, observer: Any) -> Any:
        """
        Attaches an observer to the subject.

        This method allows registering an observer object to monitor
        and react to changes or updates made to the subject.

        :param observer: The observer object to be attached. It must conform
            to the expected interface required to receive updates.
        :return: None
        """
        pass

    def detach(self, observer: Any) -> Any:
        """
        Detach the provided observer from the current set of observers if it is
        present. This method ensures the observer will no longer receive updates from
        this subject.

        :param observer: The observer to be removed from the set of observers.
        :type observer: Any
        :return: None
        """
        pass

    def notify(self, message: Any) -> Any:
        """
        Notifies the system or a user with a provided message.

        :param message: The message content to be sent as notification
        :type message: Any
        :return: The result of the notification process
        :rtype: Any
        """
        pass
