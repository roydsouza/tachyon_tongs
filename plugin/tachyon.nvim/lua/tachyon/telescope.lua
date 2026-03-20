-- Tachyon Tongs: Telescope Integration
local M = {}
local api = require('tachyon.api')

M.catalog = function(opts)
    local pickers = require("telescope.pickers")
    local finders = require("telescope.finders")
    local conf = require("telescope.config").values
    local actions = require("telescope.actions")
    local action_state = require("telescope.actions.state")

    api.get("/airlock", function(data)
        if not data then return end
        
        pickers.new(opts, {
            prompt_title = "Tachyon Exploitation Catalog",
            finder = finders.new_table({
                results = data,
                entry_maker = function(entry)
                    return {
                        value = entry,
                        display = entry.cve .. " | " .. entry.status:upper() .. " | " .. entry.summary,
                        ordinal = entry.cve .. " " .. entry.summary,
                    }
                end,
            }),
            sorter = conf.generic_sorter(opts),
            attach_mappings = function(prompt_bufnr, map)
                actions.select_default:replace(function()
                    actions.close(prompt_bufnr)
                    local selection = action_state.get_selected_entry()
                    print("Inspecting CVE: " .. selection.value.cve)
                end)
                return true
            end,
        }):find()
    end)
end

return M
