-- player.lua: Simple but robust HUD and effects system

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

-- Get colors based on effects
local function get_colors()
    for _, effect in ipairs(config.effects or {}) do
        if effect:match("vhs") then
            return {primary = "FFAA00", accent = "FFFF88", bg = "000000"}
        end
    end
    return {primary = "00FFFF", accent = "00FF00", bg = "000000"} -- Cyberpunk
end

-- Create HUD display
local function create_hud_display()
    if not hud_enabled then return "" end

    local colors = get_colors()
    local hud_data = {
        get_current_time(),
        get_cpu_usage(),
        get_memory_usage(),
        get_uptime()
    }

    local position = config.hud.position or "top"
    local alignment = (position == "top") and 8 or 2

    local style = string.format(
        "{\\an%d\\fs20\\c&H%s&\\3c&H%s&\\bord2\\shad1}",
        alignment,
        colors.primary,
        colors.bg
    )

    return style .. table.concat(hud_data, "  |  ")
end

-- Update HUD
local function update_hud()
    local hud_text = create_hud_display()
    mp.set_property("sub-text", hud_text)
end

-- Show message
local function show_message()
    if #messages < 1 then return end

    local idx = math.random(#messages)
    local colors = get_colors()

    local styled_message = string.format(
        "{\\an8\\fs24\\c&H%s&\\3c&H%s&\\bord2\\shad1}%s",
        colors.accent,
        colors.bg,
        messages[idx]
    )

    mp.osd_message(styled_message, config.messages.duration or 5)
end

-- Toggle HUD
local function toggle_hud()
    hud_enabled = not hud_enabled
    if hud_enabled then
        mp.osd_message("HUD Enabled", 2)
        update_hud()
    else
        mp.osd_message("HUD Disabled", 2)
        mp.set_property("sub-text", "")
    end
end

-- Initialize
local function initialize()
    mp.msg.info("VideoWall Enhanced Player Starting...")

    load_config()
    load_messages()

    -- Start HUD timer
    if hud_timer then hud_timer:kill() end
    hud_timer = mp.add_periodic_timer(opts.hud_interval, update_hud)
    update_hud() -- Show immediately

    -- Start message timer
    if #messages > 0 and config.messages.interval > 0 then
        mp.add_periodic_timer(config.messages.interval, show_message)
        mp.add_timeout(3, show_message) -- First message after 3 seconds
    end

    -- Apply video effects
    for _, effect in ipairs(config.effects or {}) do
        if effect == "cyberpunk-glow" then
            mp.set_property("vf", "eq=brightness=0.1:contrast=1.2:saturation=1.3")
        elseif effect == "vhs-clean" then
            mp.set_property("vf", "eq=brightness=-0.05:contrast=0.9:saturation=0.8")
        end
    end

    mp.msg.info("VideoWall Enhanced Player Ready!")
end

-- Key bindings
mp.add_key_binding(opts.show_key, "show_message", show_message)
mp.add_key_binding(opts.toggle_hud_key, "toggle_hud", toggle_hud)
mp.add_key_binding(opts.reload_key, "reload_config", function()
    load_config()
    load_messages()
    update_hud()
    mp.osd_message("Config reloaded", 2)
end)

-- Initialize when file loads
mp.register_event("file-loaded", initialize)

-- Seed random
math.randomseed(os.time())

