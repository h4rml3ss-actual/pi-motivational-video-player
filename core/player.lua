-- player.lua: mpv overlay and message logic

local mp = require 'mp'
local options = require 'mp.options'
local utils = require 'mp.utils'

local opts = {
    -- Path to message file (one message per line, '#' comments allowed)
    message_file = "~/.config/videowall/messages/default.txt",
    -- Interval (seconds) between automatic messages; 0 to disable
    interval = 30,
    -- Duration (seconds) for each OSD display
    duration = 5,
    -- Hotkey to manually show a random message
    show_key = "m",
    -- Hotkey to reload the message file
    reload_key = "r",
}
options.read_options(opts, "player")
opts.message_file = utils.expand_path(opts.message_file)

-- Seed random for message selection
math.randomseed(os.time())

-- Load and parse messages from the file
local messages = {}
local function load_messages()
    messages = {}
    local f, err = io.open(opts.message_file, "r")
    if not f then
        mp.msg.warn("player.lua: could not open message file: " .. tostring(err))
        return
    end
    for line in f:lines() do
        local msg = line:match("^%s*(.-)%s*$")
        if msg ~= "" and not msg:match("^#") then
            table.insert(messages, msg)
        end
    end
    f:close()
    mp.msg.info(string.format("player.lua: loaded %d messages from %s", #messages, opts.message_file))
end

-- Display a random message via OSD/ASS
local function show_message()
    if #messages < 1 then
        mp.msg.warn("player.lua: no messages to display")
        return
    end
    local idx = math.random(#messages)
    mp.osd_message(messages[idx], opts.duration)
end

-- Manual key binding to show a message
mp.add_key_binding(opts.show_key, "show_message", show_message)

-- Manual key binding to reload messages
mp.add_key_binding(opts.reload_key, "reload_messages", function()
    load_messages()
    mp.osd_message(string.format("Messages reloaded (%d)", #messages), 2)
end)

-- Periodic timer for automatic messages
if opts.interval > 0 then
    load_messages()
    local timer = mp.add_periodic_timer(opts.interval, show_message)
    -- ensure messages are loaded once at start
    show_message()
end
