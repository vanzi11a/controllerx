import json
from typing import Any

from appdaemon.plugins.mqtt.mqttapi import Mqtt
from cx_const import DefaultActionsMapping
from cx_core.integration import EventData, Integration

PRIORITY_KEYS = ["command", "state"]


class MiLightIntegration(Integration):
    name = "milight"

    def get_default_actions_mapping(self) -> DefaultActionsMapping | None:
        return self.controller.get_milight_actions_mapping()

    async def listen_changes(self, controller_id: str) -> None:
        await Mqtt.listen_event(
            self.controller, self.event_callback, topic=controller_id, namespace="mqtt"
        )

    async def event_callback(
        self, event_name: str, data: EventData, kwargs: dict[str, Any]
    ) -> None:
        self.controller.log(f"MiLight MQTT data event: {data}", level="DEBUG")
        if "payload" not in data:
            return
        try:
            payload = json.loads(data["payload"])
        except json.decoder.JSONDecodeError:
            raise ValueError(
                f"Following MiLight payload is not valid JSON: {data['payload']}"
            )
        action_key: str | None = None
        remaining_keys = [k for k in payload if k not in PRIORITY_KEYS]
        for key in PRIORITY_KEYS + remaining_keys:
            if key in payload:
                action_key = f"{key}:{str(payload[key]).lower()}"
                break
        if action_key is None:
            self.controller.log(
                "⚠️ MiLight payload is empty, no action key found",
                level="WARNING",
                ascii_encode=False,
            )
            return
        await self.controller.handle_action(action_key, extra=payload)
