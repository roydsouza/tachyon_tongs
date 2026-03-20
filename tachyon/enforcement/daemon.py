from fastapi import FastAPI
        import pandas as pd
        import numpy as np
        
        app = FastAPI()
        
        @app.post("/eval")
        async def eval_endpoint(data: dict):
            # Evaluate the input data
            eval_data = data["eval"]
            try:
                # Attempt to evaluate the input data
                eval_result = eval(eval_data)
                return {"result": eval_result}
            except Exception as e:
                # Log the exception and return an error message
                print(f"Error evaluating input: {e}")
                return {"error": "Failed to evaluate input"}