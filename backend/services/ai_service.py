import openai
import os
from typing import Optional
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """Service class for AI operations using OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def generate_filter_code(self, prompt: str, sample_df: str) -> str:
        """
        Generate pandas filter code using OpenAI
        
        Args:
            prompt: Natural language prompt for filtering
            sample_df: String representation of sample dataframe
            
        Returns:
            Generated pandas filter code
        """
        try:
            system_message = {
                "role": "system",
                "content": """
                You are a helpful assistant. The user will give a natural language prompt and a sample of a Pandas DataFrame called `df`.

                Your job is to return a single, valid line of Python code that filters `df` using Pandas. 

                - Use `.str.contains(..., case=False, na=False)` for fuzzy, case-insensitive matching.
                - Expand common slangs or abbreviations for positions. For example:
                  - "SDE" → "Software Development Engineer"
                  - "HR" → "Human Resources", "Talent", "Recruiter", "People"
                  - "PM" → "Product Manager", "Program Manager"
                  - "TA" → "Talent Acquisition"
                  - "SDM" → "Software Development Manager"
                  - "Engg Mgr" → "Engineering Manager"
                - If the user asks for a role like "HR", include all relevant variants using a regex pattern like `'HR|Talent|Recruiter|People'`.
                - Use `&` and `|` for combining filters.
                - Do not include markdown (```), quotes, or explanations. Output only the raw Python code that starts with: `df = df[...]`
                """
            }
            
            user_message = {
                "role": "user",
                "content": f"Prompt: {prompt}\n\nSample DataFrame:\n{sample_df}"
            }
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[system_message, user_message],
                temperature=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating filter code: {str(e)}")
            raise
    
    def validate_filter_code(self, code: str) -> bool:
        """
        Basic validation of generated filter code
        
        Args:
            code: Generated pandas filter code
            
        Returns:
            True if code appears valid
        """
        try:
            # Basic checks
            if not code.startswith("df = df["):
                return False
            
            # Try to compile the code (basic syntax check)
            compile(code, '<string>', 'exec')
            return True
            
        except Exception:
            return False 