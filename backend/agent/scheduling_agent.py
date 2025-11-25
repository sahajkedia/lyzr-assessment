"""
Main scheduling agent with LLM integration and tool calling.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from backend.agent.prompts import SYSTEM_PROMPT, FAQ_CONTEXT_PROMPT
from backend.tools.availability_tool import (
    check_availability,
    get_next_available_slots,
    AVAILABILITY_TOOLS
)
from backend.tools.booking_tool import (
    book_appointment,
    BOOKING_TOOLS
)
from backend.rag.faq_rag import faq_rag
from backend.models.schemas import ChatMessage


class SchedulingAgent:
    """Intelligent scheduling agent with LLM and tools."""
    
    def __init__(self, llm_provider: str = "openai", model: str = "gpt-4-turbo"):
        """
        Initialize the scheduling agent.
        
        Args:
            llm_provider: LLM provider (openai or anthropic)
            model: Model name
        """
        self.llm_provider = llm_provider.lower()
        self.model = model
        
        # Initialize LLM client
        if self.llm_provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.llm_provider == "anthropic":
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        # Initialize FAQ RAG
        self.faq_rag = faq_rag
        
        # Available tools
        self.tools = AVAILABILITY_TOOLS + BOOKING_TOOLS
        
        # Tool function mapping
        self.tool_functions = {
            "check_availability": check_availability,
            "get_next_available_slots": get_next_available_slots,
            "book_appointment": book_appointment
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt with current date/time."""
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        return SYSTEM_PROMPT + f"\n\nCurrent date and time: {current_datetime}"
    
    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call OpenAI API."""
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**kwargs)
            
            # Extract response
            message = response.choices[0].message
            
            result = {
                "content": message.content or "",
                "tool_calls": []
            }
            
            # Handle tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    })
            
            return result
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            raise
    
    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call Anthropic API."""
        try:
            # Convert tools to Anthropic format
            anthropic_tools = []
            if tools:
                for tool in tools:
                    anthropic_tools.append({
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"]
                    })
            
            kwargs = {
                "model": self.model,
                "max_tokens": 2048,
                "messages": messages,
                "temperature": 0.7,
            }
            
            if anthropic_tools:
                kwargs["tools"] = anthropic_tools
            
            response = await self.client.messages.create(**kwargs)
            
            result = {
                "content": "",
                "tool_calls": []
            }
            
            # Extract content and tool calls
            for block in response.content:
                if block.type == "text":
                    result["content"] += block.text
                elif block.type == "tool_use":
                    result["tool_calls"].append({
                        "id": block.id,
                        "name": block.name,
                        "arguments": block.input
                    })
            
            return result
        except Exception as e:
            print(f"Error calling Anthropic: {e}")
            raise
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Call the appropriate LLM based on provider."""
        if self.llm_provider == "openai":
            return await self._call_openai(messages, tools)
        elif self.llm_provider == "anthropic":
            return await self._call_anthropic(messages, tools)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool function."""
        if tool_name not in self.tool_functions:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            func = self.tool_functions[tool_name]
            result = await func(**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Execute tool calls and add results to messages."""
        # Add assistant message with tool calls to history
        if self.llm_provider == "openai":
            # For OpenAI, we need to add the assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in tool_calls
                ]
            })
        else:  # anthropic
            # For Anthropic, add assistant message with tool_use blocks
            messages.append({
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "input": tc["arguments"]
                    }
                    for tc in tool_calls
                ]
            })
        
        # Execute tools and add results
        if self.llm_provider == "openai":
            # OpenAI format: individual tool messages
            for tool_call in tool_calls:
                result = await self._execute_tool(tool_call["name"], tool_call["arguments"])
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
        else:  # anthropic
            # Anthropic format: single user message with tool_result blocks
            tool_results = []
            for tool_call in tool_calls:
                result = await self._execute_tool(tool_call["name"], tool_call["arguments"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call["id"],
                    "content": json.dumps(result)
                })
            
            messages.append({
                "role": "user",
                "content": tool_results
            })
        
        return messages
    
    def _check_if_faq_question(self, user_message: str) -> bool:
        """Check if the user's message is likely an FAQ question."""
        faq_keywords = [
            "insurance", "cost", "price", "payment", "parking", "location",
            "address", "hours", "open", "closed", "what to bring", "bring",
            "cancel", "reschedule", "policy", "covid", "mask", "documents",
            "id", "required", "first visit", "directions", "how to get"
        ]
        
        message_lower = user_message.lower()
        
        # Check for question patterns
        is_question = any(q in message_lower for q in ["?", "what", "where", "when", "how", "do you", "can i", "is there"])
        
        # Check for FAQ keywords
        has_faq_keyword = any(keyword in message_lower for keyword in faq_keywords)
        
        return is_question and has_faq_keyword
    
    async def _get_faq_context(self, question: str) -> str:
        """Get FAQ context from RAG system."""
        faq_result = self.faq_rag.answer_question(question)
        return faq_result["context"]
    
    async def process_message(
        self,
        user_message: str,
        conversation_history: List[ChatMessage]
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary with response and updated history
        """
        # Convert conversation history to message format
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        for msg in conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Check if this is an FAQ question
        is_faq = self._check_if_faq_question(user_message)
        
        if is_faq:
            # Get FAQ context
            faq_context = await self._get_faq_context(user_message)
            
            # Add FAQ context to the conversation
            faq_prompt = FAQ_CONTEXT_PROMPT.format(
                context=faq_context,
                question=user_message
            )
            
            messages.append({
                "role": "system",
                "content": faq_prompt
            })
        
        # Call LLM (with tools for non-FAQ or mixed scenarios)
        max_iterations = 5
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # Call LLM with tools
            response = await self._call_llm(messages, tools=self.tools)
            
            # If no tool calls, we're done
            if not response["tool_calls"]:
                return {
                    "response": response["content"],
                    "metadata": {
                        "iterations": iterations,
                        "used_tools": False
                    }
                }
            
            # Execute tool calls
            messages = await self._handle_tool_calls(response["tool_calls"], messages)
            
            # Get final response after tool execution
            final_response = await self._call_llm(messages, tools=None)
            
            if not final_response["tool_calls"]:
                return {
                    "response": final_response["content"],
                    "metadata": {
                        "iterations": iterations,
                        "used_tools": True,
                        "tool_calls": [tc["name"] for tc in response["tool_calls"]]
                    }
                }
        
        # Max iterations reached
        return {
            "response": "I apologize, but I'm having trouble processing your request. Could you please rephrase or try again?",
            "metadata": {
                "iterations": iterations,
                "error": "max_iterations_reached"
            }
        }


# Global agent instance (will be initialized in main.py)
agent: Optional[SchedulingAgent] = None


def initialize_agent(llm_provider: str = None, model: str = None):
    """Initialize the global agent instance."""
    global agent
    
    if llm_provider is None:
        llm_provider = os.getenv("LLM_PROVIDER", "openai")
    
    if model is None:
        model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    agent = SchedulingAgent(llm_provider=llm_provider, model=model)
    return agent

