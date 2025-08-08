-- clock.lua: Clock HUD module placeholder

-- clock.lua: Clock HUD module

local clock = {}

--- Get current date/time string
function clock.get()
    return os.date("%Y-%m-%d %H:%M:%S")
end

return clock
