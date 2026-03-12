import pytest
from appdaemon.plugins.mqtt.mqttapi import Mqtt
from cx_core.controller import Controller
from cx_core.integration import EventData
from cx_core.integration.milight import MiLightIntegration
from pytest_mock.plugin import MockerFixture

from tests.test_utils import wrap_execution


@pytest.mark.parametrize(
    "data, expected_action, expected_extra, error_expected",
    [
        # command key takes priority
        (
            {"payload": '{"command":"brightness_down"}'},
            "command:brightness_down",
            {"command": "brightness_down"},
            False,
        ),
        # state key as second priority
        (
            {"payload": '{"state":"OFF"}'},
            "state:off",
            {"state": "OFF"},
            False,
        ),
        # value is lowercased
        (
            {"payload": '{"state":"ON"}'},
            "state:on",
            {"state": "ON"},
            False,
        ),
        # command takes priority over state when both present
        (
            {"payload": '{"state":"ON","command":"toggle"}'},
            "command:toggle",
            {"state": "ON", "command": "toggle"},
            False,
        ),
        # fallback to any key when neither command nor state present
        (
            {"payload": '{"brightness":128}'},
            "brightness:128",
            {"brightness": 128},
            False,
        ),
        # no payload key → no action called
        (
            {},
            None,
            None,
            False,
        ),
        # invalid JSON → ValueError
        (
            {"payload": "not_json"},
            None,
            None,
            True,
        ),
    ],
)
async def test_callback(
    fake_controller: Controller,
    mocker: MockerFixture,
    data: EventData,
    expected_action: str | None,
    expected_extra: dict[str, object] | None,
    error_expected: bool,
) -> None:
    handle_action_patch = mocker.patch.object(fake_controller, "handle_action")
    milight_integration = MiLightIntegration(fake_controller, {})

    with wrap_execution(error_expected=error_expected, exception=ValueError):
        await milight_integration.event_callback("test", data, {})

    if expected_action is not None:
        handle_action_patch.assert_called_once_with(
            expected_action, extra=expected_extra
        )
    else:
        handle_action_patch.assert_not_called()


async def test_listen_changes(
    fake_controller: Controller,
    mocker: MockerFixture,
) -> None:
    controller_id = "milight/states/0x1234/1"
    listen_event_mock = mocker.patch.object(Mqtt, "listen_event")
    milight_integration = MiLightIntegration(fake_controller, {})

    await milight_integration.listen_changes(controller_id)

    listen_event_mock.assert_called_once_with(
        fake_controller,
        milight_integration.event_callback,
        topic=controller_id,
        namespace="mqtt",
    )
