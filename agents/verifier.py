import json
from typing import Dict, List, Any
from llm.llm_client import LLMClient

class VerifierAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def verify_results(self, original_request: str, plan: Dict[str, Any], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        verification = self._llm_verify(original_request, plan, execution_results)
        formatted_output = self._format_output(original_request, execution_results, verification)
        
        return {
            "is_complete": execution_results["status"] == "success" and verification.get("is_complete", False),
            "verification_details": verification,
            "formatted_output": formatted_output
        }
    
    def _llm_verify(self, request: str, plan: Dict, results: Dict) -> Dict:
        system_prompt = """You are a verification agent. Analyze if the execution results adequately address the user's original request.

Respond with JSON in this exact format:
{
    "is_complete": true/false,
    "completeness_score": 0-100,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1", "suggestion2"]
}

Criteria:
- is_complete: true if all requested information was obtained successfully
- completeness_score: percentage of how well the request was fulfilled
- issues: list of any problems or missing information
- suggestions: recommendations for improvement (can be empty)"""

        user_prompt = f"""Original Request: {request}

Planned Steps:
{json.dumps(plan, indent=2)}

Execution Results:
{json.dumps(results, default=str, indent=2)}

Evaluate if the execution results satisfy the original request."""

        try:
            verification = self.llm.generate_structured_output(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                json_schema=True,
                temperature=0.2
            )
            return verification
        except Exception as e:
            return {
                "is_complete": results["status"] == "success",
                "completeness_score": 100 if results["status"] == "success" else 50,
                "issues": [str(e)],
                "suggestions": []
            }
    
    def _format_output(self, request: str, results: Dict, verification: Dict) -> Dict:
        all_data = []
        
        for step in results.get("steps", []):
            if step["status"] == "success" and step["data"]:
                all_data.append({
                    "action": step["action"],
                    "data": step["data"]
                })
        
        summary = self._generate_summary(request, results, verification)
        structured_data = self._structure_data(all_data)
        
        return {
            "summary": summary,
            "data": structured_data,
            "verification": verification
        }
    
    def _generate_summary(self, request: str, results: Dict, verification: Dict) -> str:
        if results["status"] == "success":
            return f"✅ Successfully completed: {request}"
        elif results["status"] == "partial_failure":
            error_count = len(results.get("errors", []))
            return f"⚠ Partially completed with {error_count} error(s): {request}"
        else:
            return f"❌ Failed to complete: {request}"
    
    def _structure_data(self, all_data: List[Dict]) -> List[Dict]:
        structured = []
        
        for item in all_data:
            action = item["action"]
            data = item["data"]
            
            if action == "github_search" and "repositories" in data:
                for repo in data["repositories"]:
                    structured.append({
                        "type": "repo",
                        "name": repo.get("name", "Unknown"),
                        "stars": repo.get("stars", 0),
                        "url": repo.get("url", ""),
                        "description": repo.get("description", "No description"),
                        "language": repo.get("language", "Unknown")
                    })
            
            elif action == "weather_get":
                city_name = data.get("city", "Unknown")
                structured.append({
                    "type": "weather",
                    "name": f"Weather in {city_name}",
                    "city": city_name,
                    "temperature": data.get("temperature", "N/A"),
                    "condition": data.get("condition", "N/A"),
                    "humidity": data.get("humidity", "N/A")
                })
        
        return structured