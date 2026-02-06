import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    def __init__(self, model: str = "gemini-2.5-flash"): 
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model
    
    def generate_structured_output(self, system_prompt: str, user_prompt: str, json_schema: Optional[Dict] = None, temperature: float = 0.7, max_tokens: int = 2000) -> Dict[str, Any]:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_schema else None
            )
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"response": content}
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")