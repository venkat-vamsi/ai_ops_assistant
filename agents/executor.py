import json
from typing import Dict, List, Any
from tools.github_tool import GitHubTool
from tools.weather_tool import WeatherTool

class ExecutorAgent:
    def __init__(self):
        self.tools = {
            "github_search": GitHubTool(),
            "weather_get": WeatherTool()
        }
        self.max_retries = 2
    
    def execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        results = {
            "status": "success",
            "plan_summary": plan.get("task_summary", ""),
            "steps": [],
            "data": {},
            "errors": []
        }
        
        step_outputs = {}
        
        for step in plan["steps"]:
            step_number = step["step_number"]
            action = step["action"]
            parameters = step["parameters"].copy()
            
            if "depends_on" in step and step["depends_on"]:
                parameters = self._resolve_dependencies(
                    parameters,
                    step["depends_on"],
                    step_outputs
                )
            
            step_result = self._execute_step(
                action,
                parameters,
                step["description"]
            )
            
            step_result.update({
                "step_number": step_number,
                "action": action,
                "description": step["description"]
            })
            
            results["steps"].append(step_result)
            
            if step_result["status"] == "success":
                step_outputs[step_number] = step_result["data"]
                results["data"][f"step_{step_number}_{action}"] = step_result["data"]
            else:
                results["status"] = "partial_failure"
                results["errors"].append({
                    "step": step_number,
                    "error": step_result.get("error", "Unknown error")
                })
        
        return results
    
    def _execute_step(self, action: str, parameters: Dict[str, Any], description: str) -> Dict[str, Any]:
        result = {
            "status": "failed",
            "data": None,
            "error": None,
            "retries": 0
        }
        
        for attempt in range(self.max_retries + 1):
            try:
                result["retries"] = attempt
                tool = self.tools.get(action)
                
                if not tool:
                    raise ValueError(f"Unknown tool: {action}")
                
                if action == "github_search":
                    data = tool.search(
                        query=parameters.get("query", ""),
                        sort=parameters.get("sort", "stars"),
                        max_results=parameters.get("max_results", 5)
                    )
                elif action == "weather_get":
                    data = tool.get_weather(
                        city=parameters.get("city", "")
                    )
                else:
                    raise ValueError(f"Unsupported action: {action}")
                
                if "error" in data:
                    raise Exception(data["error"])
                
                result.update({
                    "status": "success",
                    "data": data,
                    "error": None
                })
                break
                
            except Exception as e:
                result["error"] = str(e)
                if attempt >= self.max_retries:
                    result["status"] = "failed"
        
        return result
    
    def _resolve_dependencies(self, parameters: Dict[str, Any], depends_on: List[int], step_outputs: Dict[int, Any]) -> Dict[str, Any]:
        resolved = parameters.copy()
        
        if "city" in resolved and resolved["city"] == "from_previous_step":
            for step_num in depends_on:
                if step_num in step_outputs:
                    data = step_outputs[step_num]
                    
                    if isinstance(data, dict):
                        if "repositories" in data and data["repositories"]:
                            location = data["repositories"][0].get("location", "San Francisco")
                            if "," in location:
                                resolved["city"] = location.split(",")[0].strip()
                            else:
                                resolved["city"] = location
                            break
                        elif "city" in data:
                            resolved["city"] = data["city"]
                            break
            
            if resolved["city"] == "from_previous_step":
                resolved["city"] = "San Francisco"
        
        return resolved