-- player.lua: Compatible HUD system for older mpv versions

local mp = require 'mp'
local options = require 'mp.options'

-- Configuration
local opts = {
    config_file = "~/.config/videowall/config.json",
    hud_interval = 2,
    show_key = "m",
    reload_key = "r",
    toggle_hud_key = "h",
}
options.read_options(opts, "player")

-- Expand path
if opts.config_file:sub(1,1) == "~" then
    opts.config_file = os.getenv("HOME") .. opts.config_file:sub(2)
end

-- Global state
local config = {}
local messages = {}
local hud_enabled = true
local hud_timer = nil

-- Simple HUD functions
local function get_cpu_usage()
    local f = io.open("/proc/loadavg", "r")
    if not f then return "CPU N/A" end
    local line = f:read("*l")
    f:close()
    local load = line:match("^([%d%.]+)")
    return string.format("CPU %.1f", tonumber(load) or 0)
end

local function get_memory_usage()
    local total, available = 0, 0
    for line in io.lines("/proc/meminfo") do
        local key, val = line:match("(%w+):%s+(%d+)")
        if key == "MemTotal" then total = tonumber(val) end
        if key == "MemAvailable" then available = tonumber(val) end
    end
    if total > 0 and available > 0 then
        local used_pct = (total - available) * 100 / total
        return string.format("MEM %.0f%%", used_pct)
    end
    return "MEM N/A"
end

local function get_current_time()
    return os.date("%H:%M:%S")
end

local function get_uptime()
    local f = io.open("/proc/uptime", "r")
    if not f then return "UP N/A" end
    local content = f:read("*l")
    f:close()
    local secs = tonumber(content:match("^(%d+)")) or 0
    local hours = math.floor(secs / 3600)
    local mins = math.floor((secs % 3600) / 60)
    return string.format("UP %dh%02dm", hours, mins)
end

-- Load simple config
local function load_config()
    local f = io.open(opts.config_file, "r")
    if not f then
        mp.msg.warn("Could not open config file, using defaults")
        config = {
            name = "Default",
            effects = {"cyberpunk-glow"},
            hud = {position = "top"},
            messages = {interval = 30, duration = 5}
        }
        return
    end

    local content = f:read("*all")
    f:close()

    -- Simple parsing
    config.name = content:match('"name"%s*:%s*"([^"]*)"') or "Default"
    config.effects = {}
    config.hud = {position = "top"}
    config.messages = {interval = 30, duration = 5}

    -- Parse effects
    local effects_str = content:match('"effects"%s*:%s*%[([^%]]*)%]')
    if effects_str then
        for effect in effects_str:gmatch('"([^"]*)"') do
            table.insert(config.effects, effect)
        end
    end

    -- Parse HUD position
    local hud_str = content:match('"hud"%s*:%s*{([^}]*)}')
    if hud_str then
        config.hud.position = hud_str:match('"position"%s*:%s*"([^"]*)"') or "top"
    end

    -- Parse messages
    local msg_str = content:match('"messages"%s*:%s*{([^}]*)}')
    if msg_str then
        config.messages.interval = tonumber(msg_str:match('"interval"%s*:%s*(%d+)')) or 30
        config.messages.duration = tonumber(msg_str:match('"duration"%s*:%s*(%d+)')) or 5
        local msg_file = msg_str:match('"message_file"%s*:%s*"([^"]*)"')
        if msg_file and msg_file:sub(1,1) == "~" then
            config.messages.file = os.getenv("HOME") .. msg_file:sub(2)
        end
    end

    mp.msg.info("Loaded config: " .. config.name)
end

-- Load messages
local function load_messages()
    messages = {}
    if not config.messages or not config.messages.file then
        return
    end

    local f = io.open(config.messages.file, "r")
    if not f then return end

    for line in f:lines() do
        local msg = line:match("^%s*(.-)%s*$")
        if msg ~= "" and not msg:match("^#") then
            table.insert(messages, msg)
        end
    end
    f:close()

    mp.msg.info(string.format("Loaded %d messages", #messages))
end

-- Show HUD using OSD message (compatible with older mpv)
local function show_hud()
    if not hud_enabled then
        return
    end

    local hud_data = {
        get_current_time(),
        get_cpu_usage(),
        get_memory_usage(),
        get_uptime()
    }

    local hud_text = table.concat(hud_data, "  |  ")

    -- Use OSD message with longer duration for persistent display
    mp.osd_message(hud_text, opts.hud_interval + 0.5)
end

-- Show message
local function show_message()
    if #messages < 1 then return end

    local idx = math.random(#messages)
    local message = messages[idx]

    -- Show message with different styling
    mp.osd_message(">> " .. message .. " <<", config.messages.duration or 5)
end

-- Toggle HUD
local function toggle_hud()
    hud_enabled = not hud_enabled
    if hud_enabled then
        mp.osd_message("HUD Enabled", 2)
        show_hud()
    else
        mp.osd_message("HUD Disabled", 2)
    end
end

-- Initialize
local function initialize()
    mp.msg.info("VideoWall Enhanced Player Starting...")

    load_config()
    load_messages()

    -- Start HUD timer
    if hud_timer then hud_timer:kill() end
    hud_timer = mp.add_periodic_timer(opts.hud_interval, show_hud)

    -- Show HUD immediately
    mp.add_timeout(1, show_hud)

    -- Start message timer
    if #messages > 0 and config.messages.interval > 0 then
        mp.add_periodic_timer(config.messages.interval, show_message)
        mp.add_timeout(5, show_message) -- First message after 5 seconds
    end

    -- Apply dramatic visual effects
    for _, effect in ipairs(config.effects or {}) do
        if effect == "cyberpunk-glow" then
            -- Cyberpunk effect: RGB shift, scanlines, high contrast, neon colors
            local cyberpunk_filter = table.concat({
                "eq=brightness=0.4:contrast=2.0:saturation=2.5:gamma=0.7",  -- High contrast neon
                "hue=h=15:s=1.3",  -- Blue/cyan shift
                "noise=alls=20:allf=t",  -- Digital noise
                "scale=iw:ih:flags=neighbor",  -- Pixelated scaling
                "drawbox=x=0:y=0:w=iw:h=2:color=cyan@0.3:t=fill",  -- Scanline effect (top)
                "drawbox=x=0:y=ih/2:w=iw:h=2:color=cyan@0.3:t=fill"  -- Scanline effect (middle)
            }, ",")
            mp.set_property("vf", cyberpunk_filter)
            mp.msg.info("Applied cyberpunk-glow effect with scanlines and RGB shift")

        elseif effect == "vhs-clean" then
            -- VHS effect: chromatic aberration, noise, color bleeding, interlacing
            local vhs_filter = table.concat({
                "eq=brightness=-0.1:contrast=0.8:saturation=0.6:gamma=1.1",  -- Faded VHS look
                "hue=h=-10:s=0.8",  -- Warm, desaturated
                "noise=alls=15:allf=t",  -- VHS noise
                "scale=iw*0.98:ih*0.98:flags=bilinear",  -- Slight blur/softness
                "pad=iw*1.02:ih*1.02:(ow-iw)/2:(oh-ih)/2:color=black",  -- Add border back
                "drawbox=x=0:y=0:w=iw:h=1:color=yellow@0.1:t=fill",  -- Horizontal lines
                "drawbox=x=0:y=ih/3:w=iw:h=1:color=yellow@0.1:t=fill",
                "drawbox=x=0:y=ih*2/3:w=iw:h=1:color=yellow@0.1:t=fill"
            }, ",")
            mp.set_property("vf", vhs_filter)
            mp.msg.info("Applied vhs-clean effect with noise and color bleeding")

        elseif effect == "cyberpunk-glitch" then
            -- Extreme glitch effect: datamoshing, RGB separation, digital artifacts
            local glitch_filter = table.concat({
                "eq=brightness=0.5:contrast=2.5:saturation=3.0:gamma=0.6",  -- Extreme contrast
                "hue=h=30:s=1.5",  -- Strong color shift
                "noise=alls=40:allf=t",  -- Heavy digital noise
                "scale=iw*1.1:ih*1.1:flags=neighbor",  -- Pixelated upscale
                "crop=iw*0.9:ih*0.9:(iw-ow)/2:(ih-oh)/2",  -- Crop back with offset
                "drawbox=x=iw*0.1:y=0:w=iw*0.8:h=5:color=red@0.5:t=fill",  -- RGB glitch lines
                "drawbox=x=iw*0.2:y=ih/2:w=iw*0.6:h=3:color=green@0.5:t=fill",
                "drawbox=x=iw*0.15:y=ih*0.8:w=iw*0.7:h=4:color=blue@0.5:t=fill"
            }, ",")
            mp.set_property("vf", glitch_filter)
            mp.msg.info("Applied cyberpunk-glitch effect with RGB separation")

        elseif effect == "vhs-glitch" then
            -- VHS glitch: tracking errors, color distortion, static
            local vhs_glitch_filter = table.concat({
                "eq=brightness=0.1:contrast=1.3:saturation=0.4:gamma=1.2",  -- Washed out VHS
                "hue=h=-20:s=0.7",  -- Warm, faded colors
                "noise=alls=30:allf=t",  -- Heavy static
                "scale=iw*0.95:ih:flags=bilinear",  -- Horizontal compression (tracking error)
                "pad=iw*1.05:ih:(ow-iw)/2:0:color=black",  -- Add black bars
                "drawbox=x=0:y=ih*0.3:w=iw:h=20:color=white@0.2:t=fill",  -- Static lines
                "drawbox=x=0:y=ih*0.7:w=iw:h=15:color=white@0.15:t=fill"
            }, ",")
            mp.set_property("vf", vhs_glitch_filter)
            mp.msg.info("Applied vhs-glitch effect with tracking errors")
        end
    end

    mp.msg.info("VideoWall Enhanced Player Ready!")
end

-- Test effects function
local function test_effects()
    local current_vf = mp.get_property("vf")
    mp.osd_message("Current video filter: " .. (current_vf or "none"), 3)
    mp.msg.info("Current video filter: " .. (current_vf or "none"))
end

-- Key bindings
mp.add_key_binding(opts.show_key, "show_message", show_message)
mp.add_key_binding(opts.toggle_hud_key, "toggle_hud", toggle_hud)
mp.add_key_binding(opts.reload_key, "reload_config", function()
    load_config()
    load_messages()
    mp.osd_message("Config reloaded", 2)
end)
mp.add_key_binding("e", "test_effects", test_effects)

-- Initialize when file loads
mp.register_event("file-loaded", initialize)

-- Seed random
math.randomseed(os.time())
