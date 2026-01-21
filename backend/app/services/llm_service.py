# ========================================
# FILE: backend/app/services/llm_service.py
# Purpose: Multi-LLM provider orchestration with automatic fallbacks
# Supports: Gemini, Euron.one, OpenAI, Anthropic, Local models
# ========================================

import google.generativeai as genai
import anthropic
import openai
import requests
from typing import Optional, List, Dict, Any, Iterator
from app.core.config import settings
import logging
import itertools

logger = logging.getLogger(__name__)

class LLMService:
    """
    Multi-provider LLM service with automatic fallback chain.
    Tries primary provider → secondary providers → local models.
    Handles multiple API keys per provider for load balancing.
    """
    
    def __init__(self):
        self.current_key_index = {
            "gemini": 0,
            "euron": 0,
            "openai": 0
        }
        
        # Initialize clients
        self._init_gemini()
        self._init_openai()
        self._init_anthropic()
    
    def _init_gemini(self):
        """Initialize Gemini with API keys"""
        keys = settings.get_gemini_keys()
        if keys:
            genai.configure(api_key=keys[0])
            logger.info(f"✅ Gemini initialized with {len(keys)} API key(s)")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        keys = settings.get_openai_keys()
        if keys:
            openai.api_key = keys[0]
            logger.info(f"✅ OpenAI initialized with {len(keys)} API key(s)")
    
    def _init_anthropic(self):
        """Initialize Anthropic client"""
        if settings.ANTHROPIC_API_KEY:
            # Updated: Use anthropic.Anthropic instead of anthropic.Client
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("✅ Anthropic initialized")
    
    def _get_next_key(self, provider: str) -> Optional[str]:
        """
        Get next API key for load balancing/fallback.
        Rotates through available keys for the provider.
        """
        if provider == "gemini":
            keys = settings.get_gemini_keys()
        elif provider == "euron":
            keys = settings.get_euron_keys()
        elif provider == "openai":
            keys = settings.get_openai_keys()
        else:
            return None
        
        if not keys:
            return None
        
        # Round-robin through keys
        key = keys[self.current_key_index[provider] % len(keys)]
        self.current_key_index[provider] += 1
        return key
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Generate text with automatic provider fallback.
        
        Fallback chain:
        1. Primary provider (from settings.LLM_PROVIDER)
        2. Gemini (if not primary)
        3. Euron.one (if not primary)
        4. OpenAI (if configured)
        5. Anthropic (if configured)
        6. Local model (if enabled) - FINAL FALLBACK
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream response
        
        Returns:
            Generated text
        """
        
        # Build fallback chain
        providers = self._build_provider_chain()
        
        last_error = None
        
        for provider in providers:
            try:
                logger.info(f"🔄 Trying {provider}...")
                
                if provider == "gemini":
                    return await self._generate_gemini(prompt, system_prompt, max_tokens, temperature)
                
                elif provider == "euron":
                    return await self._generate_euron(prompt, system_prompt, max_tokens, temperature)
                
                elif provider == "openai":
                    return await self._generate_openai(prompt, system_prompt, max_tokens, temperature)
                
                elif provider == "anthropic":
                    return await self._generate_anthropic(prompt, system_prompt, max_tokens, temperature)
                
                elif provider == "local":
                    return await self._generate_local(prompt, system_prompt, max_tokens, temperature)
                
            except Exception as e:
                logger.error(f"❌ {provider} failed: {str(e)}")
                last_error = e
                continue
        
        # All providers failed
        raise Exception(f"All LLM providers failed. Last error: {last_error}")
    
    def _build_provider_chain(self) -> List[str]:
        """Build the fallback provider chain - LOCAL IS LAST"""
        chain = [settings.LLM_PROVIDER]
        
        # Add other providers (local is intentionally last)
        for provider in ["gemini", "euron", "openai", "anthropic"]:
            if provider not in chain:
                # Check if provider is configured
                if provider == "gemini" and settings.get_gemini_keys():
                    chain.append(provider)
                elif provider == "euron" and settings.get_euron_keys():
                    chain.append(provider)
                elif provider == "openai" and settings.get_openai_keys():
                    chain.append(provider)
                elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
                    chain.append(provider)
        
        # Add local as FINAL fallback
        if settings.USE_LOCAL_LLM and "local" not in chain:
            chain.append("local")
        
        logger.info(f"📋 LLM Fallback chain: {' → '.join(chain)}")
        return chain
    
    async def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Gemini"""
        key = self._get_next_key("gemini")
        if not key:
            raise ValueError("No Gemini API key available")
        
        genai.configure(api_key=key)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Combine system + user prompt
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        return response.text
    
    async def _generate_euron(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Euron.one API"""
        key = self._get_next_key("euron")
        if not key:
            raise ValueError("No Euron API key available")
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Make request
        response = requests.post(
            f"{settings.EURON_BASE_URL}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            },
            json={
                "model": settings.EURON_CHAT_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=300
        )
        
        response.raise_for_status()
        data = response.json()
        
        # Extract text from response
        return data["choices"][0]["message"]["content"]
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using OpenAI v1.0+ API"""
        from openai import OpenAI
        
        key = self._get_next_key("openai")
        if not key:
            raise ValueError("No OpenAI API key available")
        
        client = OpenAI(api_key=key)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using Anthropic Claude"""
        message = self.anthropic_client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else "You are a helpful assistant.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
    async def _generate_local(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> str:
        """Generate using local Ollama model"""
        # Use Ollama API
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{settings.LOCAL_LLM_URL}/api/chat",
            json={
                "model": "mistral",  # CHANGED from llama3.2:3b to mistral
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=120
        )
        
        response.raise_for_status()
        data = response.json()
        
        return data["message"]["content"]
    

# Create global instances
llm_service = LLMService()