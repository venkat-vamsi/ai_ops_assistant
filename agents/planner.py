import json
from typing import Dict, List, Any
from llm.llm_client import LLMClient

class PlannerAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.available_tools = {
            "github_search": {
                "description": "Search GitHub repositories by query, sort by stars/forks/updated, get repository details",
                "parameters": {
                    "query": "Search query (e.g., 'python machine learning', 'javascript react')",
                    "sort": "Sort by: stars, forks, or updated (default: stars)",
                    "max_results": "Maximum number of results to return (default: 5, max: 10)"
                },
                "examples": [
                    "Find top Python repos",
                    "Search for machine learning projects",
                    "Find React repositories sorted by stars"
                ]
            },
            "weather_get": {
                "description": "Get current weather information for a city including temperature, conditions, and humidity",
                "parameters": {
                    "city": "City name (e.g., 'New York', 'London', 'Tokyo')"
                },
                "examples": [
                    "Get weather in New York",
                    "Check temperature in London",
                    "What's the weather in Tokyo"
                ]
            }
        }
    
    def create_plan(self, user_request: str) -> Dict[str, Any]:
        system_prompt = self._build_system_prompt()
        user_prompt = f"User request: {user_request}\n\nCreate a detailed execution plan for this request."
        
        try:
            plan = self.llm.generate_structured_output(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_schema=True,
                temperature=0.3
            )
            
            self._validate_plan(plan)
            return plan
            
        except Exception as e:
            raise Exception(f"Failed to create plan: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        return f"""You are a task planning agent. Your job is to break down user requests into executable steps.

Available tools:
{json.dumps(self.available_tools, indent=2)}

IMPORTANT: You must respond with valid JSON in this exact format:
{{
    "task_summary": "Brief summary of what the user wants",
    "steps": [
        {{
            "step_number": 1,
            "action": "tool_name (must be one of: github_search, weather_get)",
            "description": "Clear description of what this step does",
            "parameters": {{
                "param_name": "param_value"
            }},
            "depends_on": []
        }}
    ],
    "expected_output": "Description of what the final result should contain"
}}

Rules:
1. step_number must start at 1 and increment
2. action must be exactly one of: github_search, weather_get
3. parameters must match the tool's required parameters
4. depends_on is an array of step numbers this step depends on (empty if no dependencies)
5. Keep plans simple and direct
6. Each step should have a clear, single purpose
7. If the user asks about weather in a location from a previous step, use "from_previous_step" as the city value

Example for "Find Python repos and check weather in NYC":
{{
    "task_summary": "Search for Python repositories and get weather information for New York City",
    "steps": [
        {{
            "step_number": 1,
            "action": "github_search",
            "description": "Search for top Python repositories",
            "parameters": {{
                "query": "python",
                "sort": "stars",
                "max_results": 5
            }},
            "depends_on": []
        }},
        {{
            "step_number": 2,
            "action": "weather_get",
            "description": "Get current weather for New York City",
            "parameters": {{
                "city": "New York"
            }},
            "depends_on": []
        }}
    ],
    "expected_output": "List of top Python repositories with their details and current weather in New York City"
}}"""
    
    def _validate_plan(self, plan: Dict[str, Any]) -> None:
        required_fields = ["task_summary", "steps", "expected_output"]
        for field in required_fields:
            if field not in plan:
                raise ValueError(f"Plan missing required field: {field}")
        
        if not isinstance(plan["steps"], list) or len(plan["steps"]) == 0:
            raise ValueError("Plan must contain at least one step")
        
        valid_actions = set(self.available_tools.keys())
        for step in plan["steps"]:
            if "action" not in step or step["action"] not in valid_actions:
                raise ValueError(f"Invalid action in step: {step.get('action')}")
            
            if "step_number" not in step or "description" not in step or "parameters" not in step:
                raise ValueError(f"Step missing required fields: {step}")