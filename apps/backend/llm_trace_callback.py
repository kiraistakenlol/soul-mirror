# LangChain callback handler to capture LLM requests and responses
from langchain_core.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List
import json

class LLMTraceCallback(BaseCallbackHandler):
    """Captures all LLM interactions during a request"""

    def __init__(self):
        self.traces = []
        self._current_request = None

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Capture LLM request"""
        self._current_request = {
            "type": "llm_call",
            "model": serialized.get("id", ["unknown"])[-1] if "id" in serialized else "unknown",
            "prompts": prompts,
            "kwargs": {k: v for k, v in kwargs.items() if k not in ["run_id", "parent_run_id", "tags"]}
        }

    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List[Any]], **kwargs: Any
    ) -> None:
        """Capture chat model request"""
        # Extract messages as dicts
        formatted_messages = []
        for message_group in messages:
            group = []
            for msg in message_group:
                if hasattr(msg, "type") and hasattr(msg, "content"):
                    group.append({
                        "role": msg.type,
                        "content": msg.content
                    })
                else:
                    group.append(str(msg))
            formatted_messages.append(group)

        self._current_request = {
            "type": "chat_model_call",
            "model": serialized.get("id", ["unknown"])[-1] if "id" in serialized else "unknown",
            "messages": formatted_messages,
            "kwargs": {k: v for k, v in kwargs.items() if k not in ["run_id", "parent_run_id", "tags"]}
        }

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Capture LLM response"""
        if self._current_request is None:
            return

        # Extract response content
        if hasattr(response, "generations"):
            generations = []
            for gen_list in response.generations:
                gen_group = []
                for gen in gen_list:
                    if hasattr(gen, "message"):
                        # Chat model response
                        msg = gen.message
                        msg_dict = {
                            "role": getattr(msg, "type", "unknown"),
                            "content": getattr(msg, "content", "")
                        }
                        # Include tool calls if present
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            msg_dict["tool_calls"] = [
                                {
                                    "name": tc.get("name", ""),
                                    "args": tc.get("args", {})
                                }
                                for tc in msg.tool_calls
                            ]
                        gen_group.append(msg_dict)
                    elif hasattr(gen, "text"):
                        gen_group.append({"text": gen.text})
                    else:
                        gen_group.append(str(gen))
                generations.append(gen_group)

            self._current_request["response"] = generations
        else:
            self._current_request["response"] = str(response)

        # Add to traces
        self.traces.append(self._current_request)
        self._current_request = None

    def get_traces(self) -> List[Dict]:
        """Get all captured traces"""
        return self.traces
