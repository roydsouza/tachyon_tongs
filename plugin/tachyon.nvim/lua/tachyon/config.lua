-- Tachyon Tongs: Plugin Configuration
local M = {}

M.defaults = {
    substrate_url = "http://localhost:60461",
    auto_refresh = true,
    refresh_interval = 2000,
    keybindings = {
        dashboard = "<leader>td",
        status = "<leader>ts",
    }
}

M.options = {}

M.setup = function(opts)
    M.options = vim.tbl_deep_extend("force", M.defaults, opts or {})
end

return M
