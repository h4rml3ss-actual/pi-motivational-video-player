-- mem.lua: Memory usage HUD module placeholder

-- mem.lua: Memory usage HUD module

local mem = {}

--- Get memory usage percentage
function mem.get()
    local info = {}
    for line in io.lines("/proc/meminfo") do
        local key, val = line:match("(%w+):%s+(%d+)")
        if key and val then
            info[key] = tonumber(val)
        end
    end
    if not info.MemTotal or not info.MemAvailable then
        return "mem N/A"
    end
    local used = info.MemTotal - info.MemAvailable
    local pct = used * 100 / info.MemTotal
    return string.format("mem %.1f%%", pct)
end

return mem
