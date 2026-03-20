local M = {}

M.ui = require('tachyon.ui')
M.api = require('tachyon.api')
M.config = require('tachyon.config')
M.telescope = require('tachyon.telescope')

M.setup = function(opts)
    M.config.setup(opts)
    require('tachyon.commands').register()
    print("Tachyon Tongs Bridge Initialized (V1 Unified)")
end

M.open_dashboard = function()
    -- Launch the interactive TUI dashboard in a floating terminal
    local buf, win = M.ui.create_float("Tachyon tactical dashboard", 0.9, 0.9)
    vim.fn.termopen("tt dash")
    vim.cmd("startinsert")
end

return M
