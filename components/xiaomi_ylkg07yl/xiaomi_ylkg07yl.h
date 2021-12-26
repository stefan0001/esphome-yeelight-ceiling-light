#pragma once

#include "esphome/components/esp32_ble_tracker/esp32_ble_tracker.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/xiaomi_ble/xiaomi_ble.h"
#include "esphome/core/automation.h"
#include "esphome/core/component.h"

#ifdef USE_ESP32

namespace esphome {
namespace xiaomi_ylkg07yl {

static const uint8_t BUTTON_ON = 0;
static const uint8_t BUTTON_OFF = 1;
static const uint8_t BUTTON_SUN = 2;
static const uint8_t BUTTON_M = 4;
static const uint8_t BUTTON_PLUS = 3;
static const uint8_t BUTTON_MINUS = 5;

class XiaomiYLKG07YL : public Component, public esp32_ble_tracker::ESPBTDeviceListener {
 public:
  void set_address(uint64_t address) { address_ = address; }
  void set_bindkey(const std::string &bindkey);

  bool parse_device(const esp32_ble_tracker::ESPBTDevice &device) override;

  void dump_config() override;
  float get_setup_priority() const override { return setup_priority::DATA; }
  void set_keycode(sensor::Sensor *keycode) { keycode_ = keycode; }
  void add_on_receive_callback(std::function<void(int)> &&callback);

 protected:
  uint64_t address_;
  uint8_t bindkey_[12];
  sensor::Sensor *keycode_{nullptr};
  CallbackManager<void(int)> receive_callback_{};

  bool decrypt_mibeacon_v23_(std::vector<uint8_t> &raw, const uint8_t *bindkey, const uint64_t &address);
};

class OnButtonOnTrigger : public Trigger<> {
 public:
  OnButtonOnTrigger(XiaomiYLKG07YL *a_remote) {
    a_remote->add_on_receive_callback([this](int keycode) {
      if (keycode == BUTTON_ON) {
        this->trigger();
      }
    });
  }
};

}  // namespace xiaomi_ylkg07yl
}  // namespace esphome

#endif
