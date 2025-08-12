-- player.lua: Enhanced mpv overlay with HUD modules and visual effects

local mp = require 'mp'
local options = require 'mp.options'
local utils = require 'mp.utils'

-- Configuration
local opts = {
    -- Path to active configuration file
    config_file = "~/.config/videowall/config.json",
    -- HUD update interval (seconds)
    hud_interval = 2,
    -- Message display settings
    message_interval = 30,
    message_duration = 5,
    -- Hotkeys
    show_key = "m",
    reload_key = "r",
    toggle_hud_key = "h",
}
options.read_options(opts, "player")

-- Handle path expansion
if opts.config_file:sub(1,1) == "~" then
    opts.config_file = os.getenv("HOME") .. opts.config_file:sub(2)
end

-- Global state
local config = {}
local hud_modules = {}
local messages = {}
local hud_enabled = true
local hud_timer = nil

-- Cyberpunk color scheme
local colors = {
    primary = "00FFFF",      -- Cyan
    secondary = "FF00FF",    -- Magenta
    accent = "00FF00",       -- Green
    warning = "FFFF00",      -- Yellow
    error = "FF0000",        -- Red
    background = "000000",   -- Black
    text = "FFFFFF",         -- White
}

-- VHS color scheme
local vhs_colors = {
    primary = "FFAA00",      -- Orange
    secondary = "AA5500",    -- Brown
    accent = "FFFF88",       -- Light Yellow
    warning = "FF8800",      -- Orange-Red
    error = "FF4444",        -- Light Red
    background = "000000",   -- Black
    text = "EEEEEE",         -- Off-White
}

-- Load JSON configuration
local function load_config()
    local f, err = io.open(opts.config_file, "r")
    if not f then
        mp.msg.warn("Could not open config file: " .. tostring(err))
        return false
    end

    local content = f:read("*all")
    f:close()

    -- Simple JSON parsing for our specific format
    local json_str = content:gsub("//.-\n", ""):gsub("/%*.-*%/", "")

    -- Parse basic JSON structure (simplified)
    config = {}
    config.name = json_str:match('"name"%s*:%s*"([^"]*)"') or "Default"
    config.effects = {}
    config.hud = { modules = {}, position = "top" }
    config.messages = { interval = 30, duration = 5 }

    -- Parse effects array
    local effects_str = json_str:match('"effects"%s*:%s*%[([^%]]*)%]')
    if effects_str then
        for effect in effects_str:gmatch('"([^"]*)"') do
            table.insert(config.effects, effect)
        end
    end

    -- Parse HUD modules
    local hud_str = json_str:match('"hud"%s*:%s*{([^}]*)}')
    if hud_str then
        local modules_str = hud_str:match('"modules"%s*:%s*%[([^%]]*)%]')
        if modules_str then
            for module in modules_str:gmatch('"([^"]*)"') do
                table.insert(config.hud.modules, module)
            end
        end
        config.hud.position = hud_str:match('"position"%s*:%s*"([^"]*)"') or "top"
    end

    -- Parse messages config
    local msg_str = json_str:match('"messages"%s*:%s*{([^}]*)}')
    if msg_str then
        config.messages.interval = tonumber(msg_str:match('"interval"%s*:%s*(%d+)')) or 30
        config.messages.duration = tonumber(msg_str:match('"duration"%s*:%s*(%d+)')) or 5
        local msg_file = msg_str:match('"message_file"%s*:%s*"([^"]*)"')
        if msg_file then
            if msg_file:sub(1,1) == "~" then
                config.messages.file = os.getenv("HOME") .. msg_file:sub(2)
            else
                config.messages.file = msg_file
            end
        end
    end

    mp.msg.info("Loaded config: " .. config.name)
    return true
end

-- Load HUD modules
local function load_hud_modules()
    hud_modules = {}
    local hud_dir = os.getenv("HOME") .. "/.config/videowall/hud/modules/"

    for _, module_name in ipairs(config.hud.modules or {}) do
        local module_path = hud_dir .. module_name .. ".lua"
        local f = io.open(module_path, "r")
        if f then
            f:close()
            local success, module = pcall(dofile, module_path)
            if success and module and module.get then
                hud_modules[module_name] = module
                mp.msg.info("Loaded HUD module: " .. module_name)
            else
                mp.msg.warn("Failed to load HUD module: " .. module_name)
            end
        else
            mp.msg.warn("HUD module file not found: " .. module_path)
        end
    end
end

-- Load messages
local function load_messages()
    messages = {}
    if not config.messages or not config.messages.file then
        return
    end

    local f, err = io.open(config.messages.file, "r")
    if not f then
        mp.msg.warn("Could not open message file: " .. tostring(err))
        return
    end

    for line in f:lines() do
        local msg = line:match("^%s*(.-)%s*$")
        if msg ~= "" and not msg:match("^#") then
            table.insert(messages, msg)
        end
    end
    f:close()

    mp.msg.info(string.format("Loaded %d messages", #messages))
end

-- Get color scheme based on effects
local function get_colors()
    for _, effect in ipairs(config.effects or {}) do
        if effect:match("vhs") then
            return vhs_colors
        end
    end
    return colors -- Default to cyberpunk
end

-- Create ASS subtitle for HUD
local function create_hud_display()
    if not hud_enabled or not next(hud_modules) then
        return ""
    end

    local current_colors = get_colors()
    local hud_lines = {}

    -- Collect HUD data
    for name, module in pairs(hud_modules) do
        local success, data = pcall(module.get)
        if success and data then
            table.insert(hud_lines, data)
        else
            table.insert(hud_lines, name .. " N/A")
        end
    end

    if #hud_lines == 0 then
        return ""
    end

    -- Position and style based on config
    local position = config.hud.position or "top"
    local ass_text = ""

    -- ASS styling
    local style = string.format(
        "{\\an%d\\fs%d\\c&H%s&\\3c&H%s&\\bord2\\shad1}",
        position == "top" and 8 or 2,  -- alignment
        24,  -- font size
        current_colors.primary,
        current_colors.background
    )

    -- Create HUD display
    if position == "top" then
        ass_text = style .. table.concat(hud_lines, "  |  ")
    elseif position == "bottom" then
        ass_text = style .. table.concat(hud_lines, "  |  ")
    elseif position == "left" then
        ass_text = style .. table.concat(hud_lines, "\\N")
    elseif position == "right" then
        ass_text = style .. table.concat(hud_lines, "\\N")
    else
        -- Distributed around edges
        local top_items = {}
        local bottom_items = {}
        for i, line in ipairs(hud_lines) do
            if i % 2 == 1 then
                table.insert(top_items, line)
            else
                table.insert(bottom_items, line)
            end
        end

        local top_style = string.format(
            "{\\an8\\fs24\\c&H%s&\\3c&H%s&\\bord2\\shad1}",
            current_colors.primary, current_colors.background
        )
        local bottom_style = string.format(
            "{\\an2\\fs24\\c&H%s&\\3c&H%s&\\bord2\\shad1}",
            current_colors.secondary, current_colors.background
        )

        ass_text = top_style .. table.concat(top_items, "  |  ")
        if #bottom_items > 0 then
            ass_text = ass_text .. "\\N\\N\\N\\N\\N\\N\\N\\N\\N\\N" ..
                      bottom_style .. table.concat(bottom_items, "  |  ")
        end
    end

    return ass_text
end

-- Update HUD display
local function update_hud()
    if not hud_enabled then
        mp.set_property("sub-text", "")
        return
    end

    local hud_text = create_hud_display()
    mp.set_property("sub-text", hud_text)
end

-- Show random message
local function show_message()
    if #messages < 1 then
        return
    end

    local idx = math.random(#messages)
    local current_colors = get_colors()

    -- Style the message with cyberpunk/VHS aesthetics
    local styled_message = string.format(
        "{\\an8\\fs28\\c&H%s&\\3c&H%s&\\bord3\\shad2}%s",
        current_colors.accent,
        current_colors.background,
        messages[idx]
    )

    mp.osd_message(styled_message, config.messages.duration or 5)
end

-- Toggle HUD display
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

-- Initialize everything
local function initialize()
    mp.msg.info("Initializing VideoWall player...")

    -- Load configuration
    if not load_config() then
        mp.msg.error("Failed to load configuration, using defaults")
        config = {
            effects = {"cyberpunk-glow"},
            hud = { modules = {"clock", "cpu", "mem"}, position = "top" },
            messages = { interval = 30, duration = 5 }
        }
    end

    -- Load modules and messages
    load_hud_modules()
    load_messages()

    -- Set up HUD timer
    if next(hud_modules) then
        hud_timer = mp.add_periodic_timer(opts.hud_interval, update_hud)
        update_hud() -- Initial display
    end

    -- Set up message timer
    if #messages > 0 and config.messages.interval > 0 then
        mp.add_periodic_timer(config.messages.interval, show_message)
        -- Show initial message after a short delay
        mp.add_timeout(3, show_message)
    end

    -- Apply visual effects
    for _, effect in ipairs(config.effects or {}) do
        if effect == "cyberpunk-glow" then
            -- Add subtle glow effect via video filters
            mp.set_property("vf", "eq=brightness=0.1:contrast=1.2:saturation=1.3")
        elseif effect == "vhs-clean" then
            -- Add VHS-style color adjustment
            mp.set_property("vf", "eq=brightness=-0.05:contrast=0.9:saturation=0.8")
        end
    end

    mp.msg.info("VideoWall player initialized successfully")
end

-- Key bindings
mp.add_key_binding(opts.show_key, "show_message", show_message)
mp.add_key_binding(opts.toggle_hud_key, "toggle_hud", toggle_hud)
mp.add_key_binding(opts.reload_key, "reload_config", function()
    load_config()
    load_hud_modules()
    load_messages()
    update_hud()
    mp.osd_message("Configuration reloaded", 2)
end)

-- Initialize when file starts playing
mp.register_event("file-loaded", initialize)

-- Seed random for message selection
math.randomseed(os.time())

