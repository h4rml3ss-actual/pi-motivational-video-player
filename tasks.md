# VideoWall Remaining Tasks

Below is a breakdown of the remaining work for the CRT Cyberpunk Video Wall project.  We can tackle these one at a time.

## 1. Core Player (Lua)
- [x] Implement `core/player.lua` to render messages via mpv OSD/ASS
- [x] Support hot-reload of message file and manual trigger hotkey

## 2. HUD Modules (Lua)
- [x] Populate `core/hud/modules/clock.lua` (time/date)
- [x] Populate `core/hud/modules/uptime.lua`
- [x] Populate `core/hud/modules/cpu.lua`
- [x] Populate `core/hud/modules/mem.lua`
- [x] Populate `core/hud/modules/net.lua`

## 3. Filters & Shaders
- [x] Flesh out video filter presets in `core/filters/presets/*.conf`
- [x] Implement CRT geometry warp shader (`core/filters/shaders/crt-geom.glsl`)
- [x] Implement bloom shader (`core/filters/shaders/bloom.glsl`)

## 4. Launcher & Configuration (Python)
- [x] Expand `bin/videowall` to load/validate JSON config at `~/.config/videowall`
- [x] Build simple TUI in `bin/videowall-launcher` for profile selection
- [x] Define and complete JSON schema in `docs/config-schema.json`
- [x] Validate user config against the schema

## 5. Profiles & Presets
- [x] Populate `presets/pure_vhs.json` with default parameters
- [x] Populate `presets/cyberpunk_hud.json` with default parameters

## 6. Testing
- [x] Add unit tests for Python modules under `tests/`
- [x] Add integration tests for Lua/OSD behavior

## 7. Documentation
- [x] Flesh out `README.md` with installation and usage instructions
- [x] Finalize `LICENSE` text
- [x] Review and update `docs/specs.md` as needed

## 8. Packaging & Install
- [ ] Implement real steps in `installers/postinstall.sh`
- [ ] Finalize `installers/systemd/user/videowall.service`

## 9. CI & Code Quality
- [ ] Configure pre-commit hooks and/or CI pipeline

---
Feel free to check off each task as we complete it.
