# home-assistant-flair-2

## Project checks

Every review covers these:

1. **Writes go to the right place.** Every new or changed Flair API write (`client.update(type, id, …)`) targets the intended resource and ID. A room action never writes to the structure unless the change says so (#5).
2. **Manual mode is untouched** unless the change is about Manual. Most entities handle Auto and Manual differently; a change to one mode must not alter the other.
3. **Shown state is always one of the offered options.** The current mode is in the mode list; a select's current value is in its options. No `None` where HA expects a value, and no new `KeyError` in code that runs on every poll (#4, #6).
4. **Missing data is handled.** Flair data can lack keys (Puck V1 vs V2 relationships, `active`, schedule IDs), so lookups use `.get`. Both puck generations are handled wherever pucks are involved.
5. **Each entity only uses its own structure's data,** so multi-structure accounts stay safe (#3).
6. **Temperature units are consistent.** Flair stores Celsius (`-c` keys). Each entity's declared unit matches the values it returns, with no conversion applied twice.
7. **Entity IDs and unique IDs don't change.** Users' automations, dashboards and HomeKit tiles depend on them. No "enabled by default" setting may depend on the current system mode (#7).
8. **The minimum HA version (`hacs.json`) and `flairaio==0.2.0` stay as they are** unless the change is meant to move them (#8 will raise the HA minimum deliberately).
9. **Tests run against real Home Assistant at the user's version** (currently 2026.11.1). Commands go through HA's own service handlers, every file compiles, and no new warnings appear.
10. **Tests never touch the real Flair account.** The Flair client is always mocked. Live behavior is checked afterwards by the user's HA session, using a read-only prompt Claude writes.
11. **Releases are consistent.** Manifest version, CHANGELOG and tag match. The user publishes releases on GitHub (this repo's automation can't push tags).
12. **No secrets or personal data** (credentials, account and room IDs, IPs) in commits, tests or GitHub comments.
