-- Tachyon Tongs: Plugin Commands
local M = {}

M.register = function()
    vim.api.nvim_create_user_command("TachyonDash", function()
        require('tachyon').open_dashboard()
    end, { desc = "Open the Tachyon Substrate Dashboard" })

    vim.api.nvim_create_user_command("TachyonStatus", function()
        require('tachyon.api').get("/status", function(data)
            print("Substrate: " .. data.status:upper() .. " | Integrity: " .. (data.integrity_verified and "✓" or "✗"))
        end)
    end, { desc = "Show quick Tachyon status" })

    vim.api.nvim_create_user_command("TachyonCatalog", function()
        require('tachyon.telescope').catalog()
    end, { desc = "Search the Exploitation Catalog via Telescope" })
end

return M
