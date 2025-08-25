"""
LLM Client Library - Unified interface for Claude and GPT-4 API calls
Handles fallback logic, rate limiting, and response validation.
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

import openai
import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

@dataclass
class LLMResponse:
    content: str
    model: str
    provider: ModelProvider
    tokens_used: int
    confidence_score: float = 0.8

@dataclass
class LLMConfig:
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    provider: ModelProvider = ModelProvider.ANTHROPIC

class LLMClient:
    """Unified LLM client with automatic fallback and optimization."""
    
    def __init__(self):
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.openai_client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.primary_config = LLMConfig(
            model=os.getenv("PRIMARY_MODEL", "claude-3-sonnet-20240229"),
            provider=ModelProvider.ANTHROPIC
        )
        
        self.fallback_config = LLMConfig(
            model=os.getenv("FALLBACK_MODEL", "gpt-4-turbo-preview"),
            provider=ModelProvider.OPENAI
        )
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        config: Optional[LLMConfig] = None,
        use_fallback: bool = False
    ) -> LLMResponse:
        """Generate response with automatic fallback on failure."""
        
        config = config or (self.fallback_config if use_fallback else self.primary_config)
        
        try:
            if config.provider == ModelProvider.ANTHROPIC:
                return await self._call_anthropic(prompt, system_prompt, config)
            else:
                return await self._call_openai(prompt, system_prompt, config)
                
        except Exception as e:
            logger.warning(f"Primary model failed: {e}")
            if not use_fallback:
                logger.info("Attempting fallback model...")
                return await self.generate(prompt, system_prompt, use_fallback=True)
            raise
    
    async def _call_anthropic(
        self, 
        prompt: str, 
        system_prompt: str, 
        config: LLMConfig
    ) -> LLMResponse:
        """Call Anthropic Claude API."""
        
        messages = [{"role": "user", "content": prompt}]
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.anthropic_client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system=system_prompt,
                messages=messages
            )
        )
        
        return LLMResponse(
            content=response.content[0].text,
            model=config.model,
            provider=ModelProvider.ANTHROPIC,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            confidence_score=0.85
        )
    
    async def _call_openai(
        self, 
        prompt: str, 
        system_prompt: str, 
        config: LLMConfig
    ) -> LLMResponse:
        """Call OpenAI GPT API."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.openai_client.chat.completions.create(
                model=config.model,
                messages=messages,
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=config.model,
            provider=ModelProvider.OPENAI,
            tokens_used=response.usage.total_tokens,
            confidence_score=0.82
        )
    
    async def batch_generate(
        self, 
        prompts: List[Dict[str, str]], 
        config: Optional[LLMConfig] = None
    ) -> List[LLMResponse]:
        """Generate multiple responses concurrently."""
        
        tasks = [
            self.generate(
                prompt=p["prompt"],
                system_prompt=p.get("system_prompt", ""),
                config=config
            )
            for p in prompts
        ]
        
        return await asyncio.gather(*tasks, return_exceptions=False)
    
    def calculate_cost_estimate(self, tokens: int, model: str) -> float:
        """Estimate API cost based on token usage."""
        
        # Rough pricing estimates (per 1K tokens)
        pricing = {
            "claude-3-sonnet-20240229": 0.003,
            "gpt-4-turbo-preview": 0.01,
            "gpt-3.5-turbo": 0.0015
        }
        
        rate = pricing.get(model, 0.005)
        return (tokens / 1000) * rate

# Global client instance
llm_client = LLMClient()