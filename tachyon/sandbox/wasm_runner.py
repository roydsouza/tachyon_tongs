import wasmtime
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("tachyon.sandbox.wasm")

class WasmRunner:
    """
    Tier 1 Hardware-Level Sandbox using Wasmtime.
    Provides a memory-safe environment for deterministic tool execution.
    """
    
    def __init__(self):
        self.engine = wasmtime.Engine()
        self.linker = wasmtime.Linker(self.engine)
        self.linker.define_wasi()

    def run_tool(self, wasm_path: str, function_name: str, *args) -> Any:
        """
        Executes a specific function in a WASM module with restricted capabilities.
        """
        if not os.path.exists(wasm_path):
            raise FileNotFoundError(f"WASM module not found: {wasm_path}")

        store = wasmtime.Store(self.engine)
        wasi_config = wasmtime.WasiConfig()
        
        # Isolation: No inherit_environ, no inherit_argv, no preopens by default
        store.set_wasi(wasi_config)

        module = wasmtime.Module.from_file(self.engine, wasm_path)
        instance = self.linker.instantiate(store, module)
        
        func = instance.exports(store).get(function_name)
        if not func:
            raise AttributeError(f"Function '{function_name}' not found in WASM module.")

        logger.info(f"Executing WASM tool: {wasm_path}::{function_name}")
        return func(store, *args)
