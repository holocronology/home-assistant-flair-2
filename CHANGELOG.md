# Changelog

All notable changes to this fork will be documented here.

This project follows [Semantic Versioning](https://semver.org/).

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
