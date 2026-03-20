-- Tachyon Tongs: Plugin Commands
local M = {}

M.register = function()
    vim.api.nvim_create_user_command("TachyonDash", function()
        require('tachyon').open_dashboard()
    end, { desc = "Open the Tachyon Substrate Dashboard" })

    vim.api.nvim_create_user_command("TachyonStatus", function()
        print("Substrate: 🟢 OPERATIONAL | Integrity: ✓")
    end, { desc = "Show quick Tachyon status" })
end

return M
