# Changelog

All notable changes to this fork will be documented here.

This project follows [Semantic Versioning](https://semver.org/).

---

## [0.1.1] - 2026-06-10

Bugfix release following a full-project code review. No new features.

### Fixed
- **HVAC control buttons crashed for Puck V2-linked units** (`button.py`): `HVACUnitControlButton.puck_data` accessed the `puck` relationship directly with no `puck2` fallback — the same bug fixed in `climate.py`/`sensor.py` back in 0.1.0b2, at a third site that was missed. The puck lookup now uses the identical V1→V2 fallback pattern, and `available` correctly reports unavailable when no puck is linked at all.
- **`Last button pressed` sensor crashed when an HVAC unit has no puck** (`sensor.py`): `available` dereferenced `puck_data` without a `None` guard. Also hardened the puck relationship lookup against a missing `puck` key and corrected the `native_value` type hint (`str`, not `float`).
- **Temperature scale selects didn't update immediately** (`select.py`): both `PuckTempScale` and `Puck2TempScale` now optimistically update the structure's `temperature-scale` attribute (which `current_option` actually reads) before writing state, so the UI reflects the change without waiting for the next poll.
- **Full data dump serialized on every poll** (`coordinator.py`): the debug log serialized the entire Flair data tree with `json.dumps` inside an f-string, paying the serialization cost on every update even with debug logging disabled. Replaced with lazy, summary-level debug logs (structure names and relationship keys).
- **Private Home Assistant API usage in reauth** (`config_flow.py`): the v1 entry migration called `config_entries._async_schedule_save()`; `unique_id` is now passed through the public `async_update_entry` instead.
- **`util.py` cleanup**: replaced the deprecated `async_timeout` package with `asyncio.timeout`; re-raise `FlairAuthError` with a bare `raise` (preserving the traceback); added messages to `NoUserError`/`NoStructuresError`; fixed a docstring copy-pasted from an unrelated integration.
- **Hardened HVAC puck lookup** (`climate.py`): the `puck` relationship key access now uses `.get()` so a structure payload without the key cannot raise `KeyError`.

### Added
- **Translation completeness**: the `issues` and `repairs`/`options` strings added during the beta cycle are now present in `strings.json` (the canonical source) and in the `hr`/`sk` locale files (English fallback text pending native translations).

### Verified (no code change needed)
- **Vent tilt snapping to 50%** (`cover.py`): flagged by review as a bug, but it is intentional — Flair vent hardware only supports 0/50/100% positions, as documented in the README.

---

## [0.1.0] - 2026-05-19

First stable release. All features introduced and refined across the b1–b6 beta cycle are considered production-ready.

### Summary of changes since upstream baseline (0.2.4)

- **Puck V2 support** — full entity coverage (sensor, binary_sensor, switch, select, number) for Puck V2 devices via the `puck2s` relationship key, which the upstream `flairaio` library does not fetch
- **HVAC puck fallback** — resolves Puck V1 via `relationships['puck']`, falling back to `relationships['puck2']` for Puck V2-linked mini-splits
- **Resilient Puck V2 fetching** — narrowed exception handling, reauth on auth failure, retains previous data on transient errors
- **Options flow** — scan interval (15–600 s) and API timeout (5–120 s) are user-configurable via Settings → Integrations → Flair → Configure
- **Set-point controller awareness** — when the set-point controller is a third-party Thermostat, the temperature slider is hidden and write attempts raise a clear `HomeAssistantError` instead of silently failing
- **HVAC structure-off display** — HVAC units correctly show Off (not their last cached mode) when the structure is set to Off in auto mode
- **Diagnostics** — full structure/device dump available via Settings → Devices & Services → Flair → Download Diagnostics; OAuth credentials auto-redacted
- **Repairs integration** — HVAC units with no associated Puck surface an actionable item in Settings → Repairs, clearing automatically once a Puck is linked
- **Smart Away switch** — `switch.<structure>_smart_away` exposes Smart Away mode as an on/off toggle for presence automations
- **Migration fallthrough fix** — version 1 migration block now correctly returns before executing the version 2 block
- **`hacs.json` fix** — removed `zip_release: true` / `filename: flair.zip` which required a GitHub Release artifact that does not exist on this fork

---

## [0.1.0b6] - 2026-05-18

### Fixed
- **All HVAC entities marked Unavailable** (`climate.py`): the `0.1.0b5` structure-off fix accidentally stacked a duplicate `@property` decorator on `HVAC.hvac_mode`, causing every HVAC entity's `state` to raise `TypeError: 'property' object is not callable` and Home Assistant to mark them unavailable. Decorator removed; HVAC entities are restored.

---

## [0.1.0b5] - 2026-05-17

### Fixed
- **HVAC units now reflect Off state when structure is off in auto mode** (`climate.py`): when the system mode is Auto and the structure is set to Off (`structure-heat-cool-mode` = `float`), individual HVAC unit climate entities were stuck showing their last cached mode (e.g. Heat) along with a misleading hvac_action icon. The `hvac_mode`, `hvac_modes`, and `hvac_action` properties now honor the structure-level off state, matching what the Flair app displays.

---

## [0.1.0b4] - 2026-05-17

### Added
- **Diagnostics support** (`diagnostics.py`): the integration now exposes a diagnostics dump via **Settings → Devices & Services → Flair → Download Diagnostics**. The report includes structure attributes, relationship keys, puck/puck2/vent/room/HVAC unit/bridge data, and current readings. OAuth credentials are automatically redacted. HVAC unit `relationships` are included in full (not just keys) to make future puck-linkage issues immediately visible without needing debug logging.
- **Repairs / issue registry integration** (`climate.py`): when a Flair HVAC unit has no associated Puck (V1 or V2), the integration now raises an actionable item in **Settings → Repairs** instead of only writing a one-shot log warning. The issue clears automatically once a Puck is linked and the next update runs.
- **Smart Away switch** (`switch.py`): a new structure-level `switch.<structure>_smart_away` entity exposes "Smart Away" mode as an on/off control, making it trivial to wire into Home Assistant presence automations (e.g. flip off when everyone is home, on when everyone leaves). Mirrors the existing `select.away_mode` ("Smart Away" / "Off Only") with a more automation-friendly surface.

### Verified (no code change needed)
- **Puck V2 ⇄ Room availability**: Room climate entities derive availability from `current-temperature-c` directly and perform no puck lookups — unaffected by the puck/puck2 relationship key distinction.
- **Long-term statistics**: all measurement sensors already carry `state_class = MEASUREMENT` and typed `native_unit_of_measurement` constants — HA long-term statistics and graphing are enabled automatically.
- **Puck V2 availability gaps**: all Puck V2 select/switch/number entities already guard optional attributes (`locked`, `puck-display-color`, `setpoint-bound-low/high`, `temperature-offset-override-c`) with `.get()` checks and properly mark themselves unavailable when those attributes are absent.

---

## [0.1.0b3] - 2026-05-17

### Added
- **Options flow for scan interval & API timeout** (`config_flow.py`, `coordinator.py`, `const.py`, `__init__.py`): configure → "Configure" on the Flair integration now opens an options form to tune polling cadence (15–600 s, default 30 s) and per-request timeout (5–120 s, default 20 s). The entry is reloaded automatically when options change.

### Changed
- **Resilient Puck V2 fetching** (`coordinator.py`): narrowed the previous broad `except Exception` around the `puck2s` and `current-reading` fetches to `FlairError` / `asyncio.TimeoutError`, with `FlairAuthError` now correctly routed to reauth. On transient failures the coordinator retains the previous successful puck2 data and current readings instead of resetting them to empty, so Puck V2 entities no longer flicker to unavailable on a single API hiccup. Warning logs now include the exception type, structure name, and how many cached devices were retained.
- **Set-point controller awareness** (`climate.py`): when the structure's set-point controller is "Thermostat", the `StructureClimate` entity now omits the `TARGET_TEMPERATURE` feature flag (so the temperature slider is hidden) and `async_set_temperature` raises a `HomeAssistantError` with actionable text instead of silently logging. Previously, temperature changes in this mode were dropped without any user-visible feedback.

---

## [0.1.0b2] - 2026-05-06

### Fixed
- **HVAC mini-splits showing "Unavailable"** (`climate.py`, `sensor.py`): the Flair API uses a separate `'puck2'` relationship key (distinct from `'puck'`) to link Puck V2 devices to HVAC units. `HVAC.puck_data` and `LastButtonPressed.puck_data` now check `relationships['puck']` first and fall back to `relationships['puck2']` when the V1 key is absent, restoring availability for all Puck V2-linked mini-split entities.

---

## [0.1.0b1] - 2026-05-05

Initial beta release of the community fork.

### Added
- **Puck V2 support** — the Flair API exposes Puck V2 devices under the `puck2s` relationship key, which the upstream `flairaio` library never fetches. The coordinator now requests `puck2s` separately after the main data update and wires full entity support into every HA platform:
  - `sensor`: Temperature, Humidity, Light, Voltage, RSSI, Pressure, Associated gateway
  - `binary_sensor`: Connection status
  - `switch`: Lock puck (conditional on device support)
  - `select`: Background color, Temperature scale (conditional on device support)
  - `number`: Set point lower limit, Set point upper limit, Temperature calibration (conditional on device support)
- `model.py` — local `Puck2` dataclass for Puck V2 device data
- Gateway lookup in `sensor.py` now also searches `puck2s` when resolving a connected gateway by ID

### Fixed
- **Migration fallthrough bug** (`__init__.py`): the `version == 1` migration block was missing a `return False`, causing it to fall through and execute the `version == 2` block as well
- **Missing `Structure` import** (`binary_sensor.py`): `Structure` was referenced in type annotations but not imported, causing a `NameError` at runtime
- **`hacs.json` zip_release** (`hacs.json`): removed `zip_release: true` and `filename: flair.zip` which required a GitHub Release artifact that does not exist on this fork

### Changed
- `const.py`: added `"puck2s": "Puck V2"` to `TYPE_TO_MODEL`
- `coordinator.py`: added debug log of raw structure relationship keys (useful for diagnosing missing device types)
- `manifest.json`, `CODEOWNERS`, `README.md`: updated to reflect fork ownership and repository URLs

---

## Upstream baseline — [0.2.4]

This fork is based on commit `12f99ff` of [RobertD502/home-assistant-flair](https://github.com/RobertD502/home-assistant-flair) at version `0.2.4`.
