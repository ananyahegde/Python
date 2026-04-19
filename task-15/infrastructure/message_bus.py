import asyncio
from collections import defaultdict


class MessageBus:
    def __init__(self):
        self._command_handlers = {}
        self._event_handlers = defaultdict(list)

    def register_command(self, command_type, handler):
        self._command_handlers[command_type] = handler

    def register_event(self, event_type, handler):
        self._event_handlers[event_type].append(handler)

    def dispatch(self, command):
        command_type = type(command)
        handler = self._command_handlers.get(command_type)
        if not handler:
            raise Exception(f"No handler registered for {command_type.__name__}")
        print(f"[WRITE] {command_type.__name__} received")
        handler.handle(command)

    def publish(self, events):
        asyncio.run(self._publish_async(events))

    async def _publish_async(self, events):
        tasks = []
        for event in events:
            event_type = type(event)
            handlers = self._event_handlers.get(event_type, [])
            for handler in handlers:
                tasks.append(handler.handle(event))
        await asyncio.gather(*tasks)
