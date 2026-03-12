from cx_const import DefaultActionsMapping, Light
from cx_core import LightController


class MiLightK2SLightController(LightController):
    def get_milight_actions_mapping(self) -> DefaultActionsMapping:
        return {
            "command:brightness_down": Light.CLICK_BRIGHTNESS_DOWN,
            "command:brightness_up": Light.CLICK_BRIGHTNESS_UP,
            "command:toggle": Light.TOGGLE,
            "command:next_mode": Light.CLICK_COLOR_TEMP_UP,
            "command:previous_mode": Light.CLICK_COLOR_TEMP_DOWN,
            "command:set_white": Light.ON_FULL_COLOR_TEMP,
            "command:night_mode": Light.ON_MIN_BRIGHTNESS,
            "state:on": Light.ON,
            "state:off": Light.OFF,
        }
