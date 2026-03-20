-- Tachyon Tongs: UI Utilities
local M = {}

M.create_float = function(title, width_ratio, height_ratio)
    local buf = vim.api.nvim_create_buf(false, true)
    local width = math.floor(vim.o.columns * (width_ratio or 0.8))
    local height = math.floor(vim.o.lines * (height_ratio or 0.8))
    
    local win = vim.api.nvim_open_win(buf, true, {
        relative = "editor",
        width = width,
        height = height,
        row = math.floor((vim.o.lines - height) / 2),
        col = math.floor((vim.o.columns - width) / 2),
        style = "minimal",
        border = "double",
        title = " " .. (title or "Tachyon") .. " ",
        title_pos = "center",
    })
    
    return buf, win
end

return M
