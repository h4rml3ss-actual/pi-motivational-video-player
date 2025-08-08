-- net.lua: Network HUD module placeholder

-- net.lua: Network usage HUD module

local net = {}

local last = {}

local function read_dev()
    local data = {}
    local f = io.open("/proc/net/dev", "r")
    if not f then return data end
    for line in f:lines() do
        local iface, stats = line:match("^%s*(%w+):%s*(.*)")
        if iface and iface ~= "lo" then
            local nums = {}
            for num in stats:gmatch("%d+") do
                table.insert(nums, tonumber(num))
            end
            -- nums[1]=rx bytes, nums[9]=tx bytes
            data[iface] = {rx = nums[1], tx = nums[9]}
        end
    end
    f:close()
    return data
end

--- Get network throughput (KB/s) per interface
function net.get()
    local now = read_dev()
    local out = {}
    for iface, vals in pairs(now) do
        local prev = last[iface] or vals
        local rx_rate = (vals.rx - prev.rx) / 1024
        local tx_rate = (vals.tx - prev.tx) / 1024
        last[iface] = vals
        table.insert(out, string.format("%s ↓%.1fKB/s ↑%.1fKB/s", iface, rx_rate, tx_rate))
    end
    return table.concat(out, " | ")
end

return net
