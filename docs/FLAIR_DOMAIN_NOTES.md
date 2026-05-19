# Flair Domain Notes

Platform-agnostic knowledge about the Flair smart-vent / smart-HVAC system, distilled from building the `home-assistant-flair-2` Home Assistant integration. The intent of this document is to make a port to another smart-home platform (e.g. Hubitat) faster by capturing API behavior, entity relationships, edge cases, and gotchas that are independent of Home Assistant's specific abstractions.

This document is **not** a copy of the Flair API reference. It is a cross-reference of "what the API says" against "what actually happens in the field" — the things you only learn by running the integration against real hardware.

---

## 1. Authentication

- **OAuth 2.0 client-credentials flow** with a per-user `client_id` and `client_secret` issued by Flair on request (https://forms.gle/VohiQjWNv9CAP2ASA).
- Tokens are short-lived; expect to refresh on a recurring cadence. Treat any auth failure as a fatal-until-reauth condition — the user must re-enter credentials.
- Credentials are sensitive. Redact them from any diagnostics dump, log file, or support attachment.

---

## 2. Entity Model

Flair organizes everything under a **Structure** (a home/building). The full type tree:

```
Structure
├── Rooms                  (logical zones the user defines in the Flair app)
│   ├── Vents              (smart vents installed in that room)
│   ├── Pucks              (V1 sensors — temperature/humidity/light/pressure)
│   └── Puck V2 (puck2s)   (next-gen pucks — same readings, different API key)
├── HVAC Units             (mini-splits, central systems — controlled via Puck IR)
├── Bridges                (Wi-Fi gateways for the mesh)
├── Thermostats            (third-party thermostats integrated with Flair)
├── Zones
└── Schedules
```

The Flair API is **JSON:API**-style. Every entity has `type`, `id`, `attributes`, and `relationships`. Relationships are how parent/child links are expressed and are the source of multiple gotchas (see §5).

### Type-to-model mapping (from `const.py`)

```
users → User
structures → Structure
rooms → Room
pucks → Puck
puck2s → Puck V2
vents → Vent
bridges → Bridge
thermostats → Thermostat
hvac-units → HVAC Unit
zones → Zone
schedules → Schedule
```

---

## 3. Structure-Level State

The Structure is the controlling object. Three attributes drive almost all higher-level behavior:

### 3.1 `mode` — System mode

Values: `"auto"` | `"manual"`

- **Auto**: Flair's "Home Evenness" algorithm runs. It opens/closes vents and (optionally) drives HVAC units to balance temperatures across rooms toward room-level targets.
- **Manual**: Each HVAC unit and vent is controlled directly by the user; Flair does not adjust anything autonomously.

**Behavioral note (from the field):** When the user flips Auto → Manual, Flair turns every HVAC unit on at its last-cached mode (e.g. "Heat"). This is Flair-side behavior, not platform-side. The integration should not try to "fix" this — just reflect it.

### 3.2 `structure-heat-cool-mode` — Auto-mode target mode

Values: `"float"` | `"heat"` | `"cool"` | `"auto"` (mapped via `ROOM_HVAC_MAP`)

This is **only meaningful when `mode == "auto"`**. It describes what the auto algorithm is currently targeting:

- `"float"` = **Off**. The structure is in Auto mode but the algorithm is dormant — no heating, no cooling, no vent adjustments.
- `"heat"` / `"cool"` / `"auto"` = the algorithm is actively driving toward heating, cooling, or both.

**Critical edge case:** When `mode == "auto"` AND `structure-heat-cool-mode == "float"`, individual HVAC unit attributes will still report their last-cached `mode` (e.g. `"Heat"`). The Flair app shows them as **Off**, but the API does not zero them out. The integration must override this client-side:

> If `structure.mode == "auto"` and `structure.structure-heat-cool-mode == "float"`, force every HVAC unit's displayed mode/action to **Off** regardless of what the unit's own `mode` attribute says.

This was the root cause of a real bug in this integration. Mirror the logic in the Hubitat port.

### 3.3 `set-point-mode` — Set-point controller

Values map via `SET_POINT_CONTROLLER`:
- `"Home Evenness For Active Rooms Follow Third Party"` → controller is a **third-party Thermostat**
- `"Home Evenness For Active Rooms Flair Setpoint"` → controller is the **Flair App**

When the controller is "Thermostat":
- The Flair app **does not allow** the user to change the structure-level setpoint — the thermostat dictates it.
- Any attempt to set a structure setpoint via the API in this state is a no-op or error.
- A good platform integration should **hide** the setpoint control surface in this mode (and explain why), not silently drop the write.

### 3.4 `structure-away-mode` — Away mode policy

Values (from `AWAY_MODES`): `"Smart Away"` | `"Off Only"`

- `"Smart Away"` — Flair uses occupancy signals (geofence, schedule, etc.) to automatically enter Away.
- `"Off Only"` — Away can only be entered manually.

Useful as an on/off toggle for presence automations.

### 3.5 Home/Away state and its setter — two separate attributes

This trips people up — verified against the real API and the HA `select.py`:

- **`home` (boolean)** is the *actual presence state*. `true` → Home, `false` → Away. This is the field to read for "is the house in Home or Away right now".
- **`home-away-mode` (enum)** is the *setter source*, despite the misleading name. Values are `"Manual"` | `"Third Party Home Away"` | `"Flair Autohome Autoaway"`, mapped via `HOME_AWAY_SET_BY` to friendly labels `"Manual"` | `"Thermostat"` | `"Flair App Geolocation"`. This controls *who is allowed to change* the home/away state, not what the state currently is.

The Hubitat driver exposes `homeAway` (from `home`) and `homeAwaySetBy` (from `home-away-mode`) to keep this distinction visible.

---

## 4. HVAC Unit Behavior

HVAC units (mini-splits and similar) are controlled by Flair via an IR-blasting **Puck** placed near the unit. The Puck "owns" the HVAC unit's state.

### 4.1 Mode mapping

Flair-side modes → standard HVAC modes (`HVAC_CURRENT_MODE_MAP`):

```
Off  → Off
Heat → Heat
Cool → Cool
Dry  → Dry
Fan  → Fan only
Auto → Heat/Cool (auto)
```

Available mode values come from each unit's `hvac-modes` attribute (a list). Always show only modes the unit advertises.

### 4.2 Fan speeds

From `HVAC_CURRENT_FAN_SPEED`: `Auto` / `High` / `Medium` / `Low`. Each unit advertises which speeds it supports.

### 4.3 Swing

Boolean-ish: `"On"` / `"Off"`. Many units don't support swing — check before exposing.

### 4.4 Active mode logic (cross-reference all three structure attributes)

This is the decision tree used to compute the displayed mode/action for each HVAC unit:

```
if structure.mode == "auto":
    if structure.structure-heat-cool-mode == "float":
        → Off (force, override unit's own mode)
    else:
        → use unit's mode attribute, mapped through HVAC_CURRENT_MODE_MAP

elif structure.mode == "manual":
    if unit.power == "Off":
        → Off
    else:
        → use unit's mode attribute, mapped through HVAC_CURRENT_MODE_MAP
```

### 4.5 Setting modes

When the user changes an HVAC unit's mode:

- In **Manual** mode: write the new mode + power state directly to the HVAC unit.
- In **Auto** mode: writes typically go to the **room** (not the HVAC unit), because Flair's auto algorithm wants to know the intent at the room level. Test against real hardware.
- Setting mode to **Off** in Manual mode writes `power: "Off"` to the unit.

---

## 5. The Puck V2 Relationship Gotcha (read carefully)

This is the single most painful API quirk in Flair.

- **Puck V1** devices are linked to HVAC units and rooms via the `"puck"` relationship key.
- **Puck V2** devices are linked via a **separate** `"puck2"` relationship key.
- The official `flairaio` Python library (as of 0.2.0) **does not fetch** `puck2s` at all.

**Implications for a port:**

1. The HTTP endpoints/JSON for Puck V2 devices are similar to V1 but live under a different relationship and a different type (`puck2s`, model name `"Puck V2"`).
2. When resolving "which Puck controls this HVAC unit?", check `relationships["puck"]` first, then fall back to `relationships["puck2"]`.
3. When resolving "which Puck is in this room?", same fallback order.
4. **Room climate availability does NOT depend on the puck relationship** — it derives from the room's own `current-temperature-c` attribute. No fallback needed there.
5. HVAC units with no associated puck (V1 or V2) cannot be controlled; surface this as a user-actionable error/repair item.

A diagnostics dump should always include the full `relationships` block for every HVAC unit (not just the keys) so this kind of linkage issue is immediately diagnosable from a support attachment.

---

## 6. Puck Attributes

Confirmed by direct observation against a real Flair account (a mix of V1
and V2 pucks). The values land in **two distinct responses** — the list
response and the `current-reading` sub-resource — and the split is not what
you'd guess from the field names alone.

### 6.1 Where each value actually lives

**From the list response** (`GET /api/structures/{id}/pucks` or `…/puck2s`,
read off `data[i].attributes`):

- `current-temperature-c` — Celsius regardless of user's preferred display unit
- `current-humidity` — percent
- `voltage` — raw volts
- `current-rssi` — **list response uses the `current-rssi` key**, not `rssi`. For
  V2 this can be null and is unreliable; use `sub-ghz-rssi` from
  current-reading instead.
- `inactive` — boolean, Flair has decided this puck is offline
- V2-only: `puck-display-color`, `temperature-scale`, `setpoint-bound-low`,
  `setpoint-bound-high`, `temperature-offset-override-c`, `locked`

**From the current-reading sub-resource** (`GET /api/pucks/{id}/current-reading`
or `…/puck2s/{id}/current-reading`, read off `data.attributes`):

- V1: `light` (must be scaled `× 2` to get lux per HA's formula `(raw/100)*200`),
  `room-pressure` (kPa, may be absent on older V1 hardware)
- V2: `sub-ghz-rssi` (the bridge radio — use this as the RSSI source for V2),
  `connected-gateway-name` (paired bridge), plus HVAC IR-signaling
  diagnostics (see §6.3)
- Both: `system-voltage`, `humidity`, `room-temperature-c` — redundant with
  the list response values, present here for freshness

### 6.2 V1 vs V2 hardware differences

V1 and V2 are different hardware classes, not just versions of the same
device:

- **V1** has a light sensor (`light`) and an air-pressure sensor
  (`room-pressure`). It does *not* transmit IR.
- **V2** has *neither* light nor pressure sensors. It *does* transmit IR to
  paired mini-split HVAC units, and its current-reading carries the IR
  signaling state (mode, fan speed, set-point, power, error).

A driver that exposes `IlluminanceMeasurement` and `PressureMeasurement`
on V2 will leave those capabilities permanently unpopulated — better to
omit them on V2 entirely.

### 6.3 V2 HVAC fields in current-reading are diagnostic, not authoritative

The V2's current-reading includes `mode-status`, `fan-speed-status`,
`power-status`, `ir-device-set-point`, `error`, etc. **These describe what
the puck is currently transmitting** to its paired IR target, not the
authoritative state of any HVAC unit. The controllable HVAC entity is a
separate `hvac-units` resource paired to the puck (§4). Surface HVAC
controls on the HVAC Unit driver, not on the V2 Puck driver — even though
the V2 is the device physically signaling IR.

### 6.4 V2 optional attributes

Many V2-only fields are optional per device and only present on hardware
that supports the feature. Always null-check and treat absence as "this
feature doesn't apply on this device" rather than reporting an error.

---

## 7. Rooms

- A Room is a user-defined logical grouping with one or more Vents and (typically) one Puck.
- Room mode is `"Active"` or `"Inactive"`. Inactive rooms are excluded from auto-mode balancing.
- Room temperature/humidity comes from `current-temperature-c` / `current-humidity-c` — **not** by looking up the puck. This is convenient: room sensors work even if the puck linkage is muddled.
- Room setpoint is `set-point-c`.

---

## 8. Vents

- Open percentage: `percent-open` (0-100).
- Vents have `inactive` like pucks.
- Writing `percent-open` only has effect in Manual mode; in Auto, the algorithm overrides.

---

## 9. Polling & API Resilience

The Flair cloud API is generally reliable but does have transient failures, especially around Puck V2 fetches (which on this integration are a separate call after the main update).

Patterns that have proven necessary:

1. **Tunable scan interval and timeout.** Defaults of 30 s / 20 s are reasonable, but heavy users want faster polling, and slow ISPs want larger timeouts. Make both user-configurable. Sensible ranges: scan 15–600 s, timeout 5–120 s.
2. **Narrow exception handling.** A bare `except Exception` will swallow auth failures and prevent reauth. Catch only the network/API exception types you actually want to retry through, and route auth errors to reauth.
3. **Retain previous data on transient failures.** If a follow-up call (e.g. the Puck V2 fetch) fails on this poll, **keep the previous good data** rather than blanking entities to unavailable on one hiccup.
4. **Log with context.** Include the structure name and the count of retained devices in warning logs — it makes "is this real or a blip?" answerable from logs alone.

---

## 10. Diagnostics: What to Capture

A "Download Diagnostics" feature should dump, redacted of credentials:

- Structure attributes
- All `relationships` keys at the structure level (raw)
- Puck, Puck V2, Vent, Room, HVAC Unit, Bridge data
- **HVAC Unit `relationships` in full** (not just keys) — this is where puck-linkage bugs hide
- Current readings (most recent poll values)

Redact at minimum: `client_id`, `client_secret`, any OAuth token, any user email.

---

## 11. Things That Look Like Bugs But Aren't

- Structure entity going **Unavailable** when system mode is Manual. The Structure entity represents the auto-mode controller; in Manual mode it has nothing to control. Use a separate System Mode select/switch surface that stays available across modes.
- All HVAC units turning on when flipping Auto → Manual. Flair-side behavior.
- HVAC unit reporting `mode: "Heat"` while the Flair app shows it as Off. See §3.2 — apply the structure-off override client-side.

---

## 12. Things That Look Like Working But Aren't

- A "set temperature" call in Thermostat-controller mode that returns 200 OK and does nothing. Always check `set-point-mode` before allowing setpoint writes from the platform side, and surface a clear error to the user instead of a silent success.
- A duplicate decorator / wrapper on the mode property in Home Assistant's case — broader lesson: anywhere the platform uses decorators or annotations to expose a property, accidental duplication can cause every entity to silently break with a low-signal error. Test the happy path on real hardware before shipping.

---

## 13. Suggested Implementation Order for a Port

If starting fresh on a new platform, this is roughly the order that minimizes rework:

1. OAuth 2.0 client-credentials auth + token refresh
2. Structure list + structure attributes (read-only)
3. Rooms + room temperature/humidity sensors
4. Pucks **and** Puck V2 (do both at once — don't defer V2, you'll just retrofit later)
5. HVAC units (read-only display first, controls after)
6. Vents (display before control)
7. Structure-level system mode select + Away mode switch
8. HVAC unit controls (mode, fan, swing, setpoint)
9. Diagnostics
10. Polling resilience (tunable interval/timeout, narrow exceptions, data retention)
11. User-actionable errors (no-puck repair item, Thermostat-controller setpoint block)

---

## 14. Reference: Existing HA Implementation

This document was distilled from `holocronology/home-assistant-flair-2`. Look at:

- `custom_components/flair/const.py` — all the literal value mappings between Flair strings and platform enums
- `custom_components/flair/coordinator.py` — polling resilience pattern (Puck V2 separate fetch + retain-on-failure)
- `custom_components/flair/climate.py` — HVAC unit mode decision tree (§4.4)
- `custom_components/flair/diagnostics.py` — what to dump and what to redact
- `CHANGELOG.md` — most entries are real-world bugs and what their root cause was; read it before starting the port

The implementation language is Python, but the **logic** is portable. Translate the decision trees, not the framework calls.
