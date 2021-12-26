import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor, esp32_ble_tracker
from esphome import automation
from esphome.const import (
    CONF_MAC_ADDRESS,
    CONF_BINDKEY,
    UNIT_EMPTY,
    ICON_EMPTY,
    DEVICE_CLASS_EMPTY,
    CONF_ID,
    CONF_TRIGGER_ID,
)

AUTO_LOAD = ["xiaomi_ble", "sensor"]
CODEOWNERS = ["@syssi"]
DEPENDENCIES = ["esp32_ble_tracker"]
MULTI_CONF = True

CONF_ON_BUTTON_ON = "on_button_on"

ON_PRESS_ACTIONS = [
    CONF_ON_BUTTON_ON,
]

xiaomi_ylkg07yl_ns = cg.esphome_ns.namespace("xiaomi_ylkg07yl")
XiaomiYLKG07YL = xiaomi_ylkg07yl_ns.class_(
    "XiaomiYLKG07YL", esp32_ble_tracker.ESPBTDeviceListener, cg.Component
)

OnButtonOnTrigger = xiaomi_ylkg07yl_ns.class_(
    "OnButtonOnTrigger", automation.Trigger.template()
)


def validate_short_bind_key(value):
    value = cv.string_strict(value)
    parts = [value[i : i + 2] for i in range(0, len(value), 2)]
    if len(parts) != 12:
        raise cv.Invalid("Bind key must consist of 12 hexadecimal numbers")
    parts_int = []
    if any(len(part) != 2 for part in parts):
        raise cv.Invalid("Bind key must be format XX")
    for part in parts:
        try:
            parts_int.append(int(part, 16))
        except ValueError:
            # pylint: disable=raise-missing-from
            raise cv.Invalid("Bind key must be hex values from 00 to FF")

    return "".join(f"{part:02X}" for part in parts_int)


CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(XiaomiYLKG07YL),
            cv.Required(CONF_MAC_ADDRESS): cv.mac_address,
            cv.Required(CONF_BINDKEY): validate_short_bind_key,
            cv.Optional(CONF_ON_BUTTON_ON): automation.validate_automation(
                {
                    cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(OnButtonOnTrigger),
                }
            ),
        }
    )
    .extend(esp32_ble_tracker.ESP_BLE_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await esp32_ble_tracker.register_ble_device(var, config)

    cg.add(var.set_address(config[CONF_MAC_ADDRESS].as_hex))
    cg.add(var.set_bindkey(config[CONF_BINDKEY]))

    for action in ON_PRESS_ACTIONS:
        for conf in config.get(action, []):
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
            await automation.build_automation(trigger, [], conf)