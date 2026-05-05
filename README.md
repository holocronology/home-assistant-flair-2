# Flair Home Assistant Integration — Community Fork

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/holocronology/home-assistant-flair-2?filename=custom_components%2Fflair%2Fmanifest.json)

This is a community-maintained fork of [RobertD502/home-assistant-flair](https://github.com/RobertD502/home-assistant-flair), adding **Puck V2** device support and ongoing improvements not available in the original integration.

> **Why this fork?** The upstream repository has been dormant since mid-2024. This fork provides active maintenance, bug fixes, and new hardware support.

---

Custom Home Assistant component for controlling and monitoring Flair structures, bridges, pucks (V1 and V2), vents, rooms, and IR HVAC units.

## Prior To Installation

You will need **OAuth 2.0** `client_id` and `client_secret` credentials.

To retrieve your credentials:
1. Log in to your Flair account at [my.flair.co](https://my.flair.co/)
2. Open the menu and choose **Account Settings**
3. Scroll down to **Developer Settings**
4. Copy your **Client ID** and **Client Secret**

If you experience any issues with credentials, [contact Flair Support](https://forms.gle/VohiQjWNv9CAP2ASA) with the email address associated with your registered Flair account.

---

# Installation

## With HACS (Recommended)

This integration is available as a **custom repository** in HACS. It is not listed in the HACS default store.

1. In Home Assistant, go to **HACS → Integrations**
2. Click the three-dot menu (top right) → **Custom repositories**
3. Enter `holocronology/home-assistant-flair-2` and select category **Integration** → click **Add**
4. Search for **Flair** in HACS → click **Download**
5. Restart Home Assistant when prompted

## Manual

Copy the `flair` directory from `custom_components` in this repository and place it inside your Home Assistant Core installation's `custom_components` directory, then restart Home Assistant.

---

# Setup

1. Navigate to **Settings → Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for `Flair` and follow the prompts to enter your Client ID and Client Secret

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=flair)

---

# Devices

Each Flair mini-split, puck (V1 and V2), room, structure, and vent is represented as a device in Home Assistant.

## Structure

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `Active Schedule` | `Select` | All schedules created in the Flair app appear here. Select "No Schedule" to disable. Disabled by default if system mode is manual. |
| `Away Mode` | `Select` | See Flair's [Away Settings](https://support.flair.co/hc/en-us/articles/360041109111-Away-Settings) docs. Disabled by default if system mode is manual. |
| `Away temperature maximum` | `Number` | Only available when set point controller is set to "Flair App". Disabled by default if system mode is manual. |
| `Away temperature minimum` | `Number` | Only available when set point controller is set to "Flair App". Disabled by default if system mode is manual. |
| `Clear home/away hold` | `Button` | Removes the time-period hold on home/away mode without reverting the mode itself. Disabled by default if system mode is manual. |
| `Default hold duration` | `Select` | Disabled by default if system mode is manual. |
| `Home/Away` | `Select` | See Flair's [Home/Away Mode](https://support.flair.co/hc/en-us/articles/360044922952-Home-Away-Mode) docs. Disabled by default if system mode is manual. |
| `Home/Away holding until` | `Sensor` | Shows time remaining on a manual home/away hold. Only available when a hold is active. Disabled by default if system mode is manual. |
| `Home/Away mode set by` | `Select` | Options: Manual, Flair App Geolocation, or Thermostat (if linked). Disabled by default if system mode is manual. |
| `Lock IR device modes` | `Switch` | Keeps heat/cool mode in sync across all IR devices. Only available if IR devices are associated with your account. |
| `Network repair mode` | `Switch` | Temporarily allows pucks and vents to connect to different gateways. Turns off automatically after 30 minutes. |
| `Reverse home/away hold` | `Button` | Removes the current hold and reverts home/away mode back to its previous state. Disabled by default if system mode is manual. |
| `Set point controller` | `Select` | Options: Flair App, or Thermostat (if linked). Disabled by default if system mode is manual. |
| `Structure` | `Climate` | Sets Flair Structure mode and set point. Target temperature only available when set point controller is "Flair App". Disabled by default if system mode is manual. |
| `System Mode` | `Select` | See Flair's [Auto](https://support.flair.co/hc/en-us/articles/360042659392-System-Auto) and [Manual](https://support.flair.co/hc/en-us/articles/360043099291-System-Manual) mode docs. |

## Bridge

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `Connection status` | `Binary Sensor` | Reports whether the bridge is online according to Flair. |
| `LED brightness` | `Number` | Brightness between 20–100. |
| `RSSI` | `Sensor` | Reports 0.0 when connected via ethernet. |

## Puck (V1)

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `Associated gateway` | `Sensor` | Name of the gateway the puck is using. Reports "Self" if the puck is acting as its own gateway. |
| `Background color` | `Select` | Set the puck background to black or white. |
| `Connection status` | `Binary Sensor` | Reports whether the puck is online according to Flair. |
| `Humidity` | `Sensor` | |
| `Light` | `Sensor` | See note below regarding light sensor accuracy. |
| `Lock puck` | `Switch` | Prevents the puck from being rotated to adjust the set point. |
| `Pressure` | `Sensor` | Room pressure reported by the puck. |
| `RSSI` | `Sensor` | |
| `Set point lower limit` | `Number` | |
| `Set point upper limit` | `Number` | |
| `Temperature` | `Sensor` | |
| `Temperature calibration` | `Number` | |
| `Temperature scale` | `Select` | |
| `Voltage` | `Sensor` | Useful for monitoring battery health. |

**Note on Puck Light Sensor**

Per Flair: *"It is not calibrated. The sensor itself, if the nominal reference is 1, can range from 0.3 to 1.6. This also doesn't take into account the mechanical loss in the Puck. In short, this is not an accurate lux sensor."*

## Puck V2

Puck V2 devices (`puck2s`) are supported in this fork. The following entities are available:

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `Associated gateway` | `Sensor` | Name of the gateway the puck is using. Reports "Self" if the puck is acting as its own gateway. |
| `Background color` | `Select` | Set the puck background to black or white. Only available if supported by the device. |
| `Connection status` | `Binary Sensor` | Reports whether the puck is online according to Flair. |
| `Humidity` | `Sensor` | |
| `Light` | `Sensor` | Only available if the device reports a light reading. |
| `Lock puck` | `Switch` | Only available if the device supports the lock attribute. |
| `Pressure` | `Sensor` | Room pressure reported by the puck. |
| `RSSI` | `Sensor` | |
| `Set point lower limit` | `Number` | Only available if the device reports setpoint bounds. |
| `Set point upper limit` | `Number` | Only available if the device reports setpoint bounds. |
| `Temperature` | `Sensor` | |
| `Temperature calibration` | `Number` | Only available if the device reports a temperature offset. |
| `Temperature scale` | `Select` | |
| `Voltage` | `Sensor` | Useful for monitoring battery health. |

> **Note:** Puck V2 was not supported in the upstream integration. This fork fetches `puck2s` as a separate resource type from the Flair API, which the upstream library (`flairaio`) does not request. Entities that depend on attributes not present on a given device will show as unavailable rather than causing errors.

## Vent

<p align="center">
  <img width="533" height="1000" src="https://github.com/holocronology/home-assistant-flair-2/blob/main/images/flair_system_setting_smaller.png?raw=true">
</p>

To control vents in Flair Rooms that have a temperature sensor, the System setting in the Flair app must be set to `Manual`. In `Auto` mode you can still send commands, but Flair will eventually override them. System mode can also be changed using the Structure's `System Mode` entity in Home Assistant.

**Vents in rooms without a temperature sensor can be controlled regardless of mode.**

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `Associated gateway` | `Sensor` | Name of the bridge or puck the vent is using as a gateway. |
| `Connection status` | `Binary Sensor` | Reports whether the vent is online according to Flair. |
| `Duct Pressure` | `Sensor` | |
| `Duct Temperature` | `Sensor` | |
| `Reported state` | `Sensor` | Disabled by default. Percent open as last reported by the vent's own sensor. Useful in automations to verify vent movement. |
| `RSSI` | `Sensor` | |
| `Vent` | `Cover` | State is `open` (50% or 100%) or `closed` (0%). Any tilt position other than 0 or 100 is interpreted as 50 due to a Flair hardware limitation. |
| `Voltage` | `Sensor` | Useful for monitoring battery health. |

## Room

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `Activity Status` | `Select` | Set room to Active or Inactive. Disabled by default if system mode is manual. |
| `Clear hold` | `Button` | Clears the temperature hold and reverts to the scheduled set point. Disabled by default if system mode is manual. |
| `Room` | `Climate` | Change temperature set point per room. Changing HVAC mode propagates to all rooms (mode is set at the Structure level). Disabled by default if system mode is manual. |
| `Temperature holding until` | `Sensor` | Time remaining on a manual temperature hold. Only available when a hold is active. Disabled by default if system mode is manual. |

Changing a room's temperature will hold for the duration set in Flair app under **Home Settings → System Settings → Default Hold Duration**, or as configured via the `Default hold duration` entity in Home Assistant.

## IR HVAC Unit

| Entity | Entity Type | Additional Comments |
|---|---|---|
| `HVAC unit` | `Climate` | See notes below. |

> **Auto Mode:** Only fan speed and swing can be controlled. Temperature set point is controlled at the room level.
>
> **Manual Mode:** Full control including HVAC mode. Setting mode to `Off` turns the unit off.

### Button-only HVAC units

For units that only expose standalone buttons in the Flair app, `Button` entities are created for each available control (Temp +, Temp -, Fan +, Fan -, etc.), plus a `Last button pressed` sensor showing the last command sent.

---

# Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

---

# Contributing / Issues

Please open issues and pull requests at [holocronology/home-assistant-flair-2](https://github.com/holocronology/home-assistant-flair-2/issues).

This fork is based on the original work by [RobertD502](https://github.com/RobertD502/home-assistant-flair). Bug fixes that apply to the upstream integration may also be submitted there.
