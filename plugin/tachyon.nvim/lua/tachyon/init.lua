-- Tachyon Tongs: NeoVim Plugin (tachyon.nvim)
-- Tier 3 of the Event-Horizon Command Bridge

local M = {}

M.setup = function(opts)
    opts = opts or {}
    local substrate_url = opts.substrate_url or "http://localhost:60461"
    
    -- Register commands
    vim.api.nvim_create_user_command("TachyonDash", function()
        M.open_dashboard()
    end, {})
    
    print("Tachyon Tongs Bridge Initialized: " .. substrate_url)
end

M.open_dashboard = function()
    -- Create a floating window running 'tt dash'
    local buf = vim.api.nvim_create_buf(false, true)
    local width = math.floor(vim.o.columns * 0.8)
    local height = math.floor(vim.o.lines * 0.8)
    
    local win = vim.api.nvim_open_win(buf, true, {
        relative = "editor",
        width = width,
        height = height,
        row = math.floor((vim.o.lines - height) / 2),
        col = math.floor((vim.o.columns - width) / 2),
        style = "minimal",
        border = "double",
    })
    
    vim.fn.termopen("tt dash")
end

return M
