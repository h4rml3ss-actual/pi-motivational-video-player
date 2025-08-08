-- uptime.lua: Uptime HUD module placeholder

-- uptime.lua: Uptime HUD module

local uptime = {}

--- Get system uptime (days/hours/minutes)
function uptime.get()
    local f = io.open("/proc/uptime", "r")
    if not f then return "uptime N/A" end
    local content = f:read("*l")
    f:close()
    local secs = tonumber(content:match("^(%d+\.?%d*)")) or 0
    local days = math.floor(secs / 86400)
    secs = secs % 86400
    local hrs = math.floor(secs / 3600)
    secs = secs % 3600
    local mins = math.floor(secs / 60)
    return string.format("uptime %dd %dh %dm", days, hrs, mins)
end

return uptime
