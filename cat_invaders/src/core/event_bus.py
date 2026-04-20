from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable


EventHandler = Callable[..., None]


class EventBus:
    """
    Простая шина событий для слабой связности между системами.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        if handler not in self._subscribers[event_name]:
            self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        handlers = self._subscribers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)

        if not handlers and event_name in self._subscribers:
            del self._subscribers[event_name]

    def emit(self, event_name: str, **payload: Any) -> None:
        handlers = list(self._subscribers.get(event_name, []))
        for handler in handlers:
            handler(**payload)

    def clear(self) -> None:
        self._subscribers.clear()