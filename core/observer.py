from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    """
    Defines an abstract base class for implementing the observer pattern.

    The Observer class serves as a base interface for objects that need to
    observe and respond to changes or notifications from other objects. It
    defines a contract that any derived class must follow by implementing
    the `update` method, which handles incoming messages or notifications.
    """

    @abstractmethod
    def update(self, message: Any) -> Any:
        """
        Update method designed to be implemented in subclasses. This method is an
        abstract method and must be overridden by any concrete subclass. It is
        responsible for processing a given `message` and optionally returning a
        processed result.

        :param message: The input message that needs to be processed.
        :type message: Any
        :return: Returns the processed result based on the implementation. The type
            of the return value depends on the subclass implementation.
        :rtype: Any
        """
        pass