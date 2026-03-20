-- Tachyon Tongs: Plugin API Client
local M = {}
local config = require('tachyon.config')

M.get = function(endpoint, callback)
    local url = config.options.substrate_url .. "/api/v1" .. endpoint
    local command = string.format("curl -s -X GET %s", url)
    
    local output = vim.fn.system(command)
    if vim.v.shell_error ~= 0 then
        vim.notify("Tachyon API Error: " .. output, vim.log.levels.ERROR)
        return nil
    end
    
    local ok, data = pcall(vim.fn.json_decode, output)
    if not ok then
        vim.notify("Tachyon API: Failed to decode JSON", vim.log.levels.ERROR)
        return nil
    end
    
    if callback then callback(data) end
    return data
end

return M
