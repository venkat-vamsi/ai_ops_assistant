import os
import requests
from typing import Dict, Any, List

class GitHubTool:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    def search(self, query: str, sort: str = "stars", max_results: int = 5) -> Dict[str, Any]:
        if not query:
            return {"error": "Query parameter is required"}
        
        if max_results > 10:
            max_results = 10
        
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": max_results
        }
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            repos = []
            for item in data.get("items", [])[:max_results]:
                repos.append({
                    "name": item.get("name"),
                    "full_name": item.get("full_name"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "language": item.get("language"),
                    "url": item.get("html_url"),
                    "description": item.get("description"),
                    "updated_at": item.get("updated_at"),
                    "owner": item.get("owner", {}).get("login")
                })
            
            return {
                "repositories": repos,
                "total_count": data.get("total_count", 0)
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"GitHub API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}