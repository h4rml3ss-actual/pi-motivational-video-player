-- cpu.lua: CPU usage HUD module placeholder

-- cpu.lua: CPU usage HUD module

local cpu = {}

local last_total, last_idle

--- Get CPU usage percentage
function cpu.get()
    local f = io.open("/proc/stat", "r")
    if not f then return "cpu N/A" end
    local line = f:read("*l")
    f:close()
    local user, nice, system, idle, iowait, irq, softirq, steal =
        line:match("cpu%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)%s+(%d+)")
    user, nice, system, idle, iowait, irq, softirq, steal =
        tonumber(user), tonumber(nice), tonumber(system), tonumber(idle),
        tonumber(iowait), tonumber(irq), tonumber(softirq), tonumber(steal)
    local total = user + nice + system + idle + iowait + irq + softirq + steal
    local diff_total = total - (last_total or total)
    local diff_idle = idle - (last_idle or idle)
    last_total = total
    last_idle = idle
    if diff_total <= 0 then return "cpu N/A" end
    local usage = (diff_total - diff_idle) * 100 / diff_total
    return string.format("cpu %.1f%%", usage)
end

return cpu
