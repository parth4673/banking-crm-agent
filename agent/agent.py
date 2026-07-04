"""
Core agent loop – orchestrates LLM reasoning with tool execution.
Uses Groq via OpenAI-compatible API.

Features:
  - Automatic retry with error feedback when tools fail
  - Input validation before tool execution
  - Real-time status callbacks for UI display
  - Execution trace for observability
"""

import json
import re
from openai import OpenAI
from agent.prompts import SYSTEM_PROMPT
from tools.registry import TOOL_DEFINITIONS, TOOL_MAP
from config import OPENAI_API_KEY, OPENAI_MODEL


# ---------------------------------------------------------------------------
# Input validation rules per tool
# ---------------------------------------------------------------------------
VALIDATION_RULES = {
    "get_customer_profile": {
        "customer_id": {"required": True, "pattern": r"^CUST\d{4}$", "message": "customer_id must be like CUST0001"},
    },
    "recommend_products": {
        "customer_id": {"required": True, "pattern": r"^CUST\d{4}$", "message": "customer_id must be like CUST0001"},
    },
    "generate_whatsapp_message": {
        "customer_id": {"required": True, "pattern": r"^CUST\d{4}$", "message": "customer_id must be like CUST0001"},
        "product_name": {"required": True, "message": "product_name is required"},
    },
    "score_conversion_likelihood": {
        "customer_ids": {"required": True, "message": "customer_ids is required (comma-separated IDs)"},
        "product_type": {"required": True, "message": "product_type is required"},
    },
    "search_customers": {
        "query": {"required": True, "message": "search query is required"},
    },
}


def validate_tool_input(tool_name: str, arguments: dict) -> list[str]:
    """
    Validate tool arguments against defined rules.
    Returns a list of error messages (empty if valid).
    """
    errors = []
    rules = VALIDATION_RULES.get(tool_name, {})

    for param, rule in rules.items():
        value = arguments.get(param)

        # Required check
        if rule.get("required") and (value is None or str(value).strip() == ""):
            errors.append(f"Missing required parameter '{param}': {rule['message']}")
            continue

        # Pattern check
        if value and rule.get("pattern"):
            if not re.match(rule["pattern"], str(value)):
                errors.append(f"Invalid '{param}': {rule['message']} (got: {value})")

    return errors


class BankingCRMAgent:
    """
    Agentic AI system for Banking CRM.

    Implements a tool-calling loop with:
    - Autonomous tool selection by the LLM
    - Input validation before execution
    - Automatic retry with error feedback
    - Real-time status updates via callback
    - Full execution trace for observability
    """

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.conversation_history: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.execution_trace: list[dict] = []

    def reset(self):
        """Clear conversation history and start fresh."""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.execution_trace = []

    def _call_llm(self) -> dict:
        """Make an API call to the LLM with current conversation and tools."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3,
        )
        return response.choices[0].message

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool with validation. Returns result or error string."""
        # Check if tool exists
        if tool_name not in TOOL_MAP:
            return json.dumps({
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(TOOL_MAP.keys()),
                "suggestion": "Please use one of the available tools listed above."
            })

        # Validate inputs
        validation_errors = validate_tool_input(tool_name, arguments)
        if validation_errors:
            return json.dumps({
                "error": "Input validation failed",
                "validation_errors": validation_errors,
                "suggestion": "Please fix the parameters and try again. "
                              "Customer IDs follow the format CUST0001-CUST0050."
            })

        # Execute
        try:
            func = TOOL_MAP[tool_name]
            result = func(**arguments)
            return result
        except TypeError as e:
            return json.dumps({
                "error": f"Wrong parameters: {str(e)}",
                "suggestion": "Check the parameter names and types, then retry."
            })
        except Exception as e:
            return json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "suggestion": "An unexpected error occurred. Try with different parameters."
            })

    def run(self, user_message: str, status_callback=None) -> dict:
        """
        Process a user message through the full agent loop.

        Args:
            user_message: The RM's question or request
            status_callback: Optional function(status_text) called at each step
                             for real-time UI updates

        Returns:
            dict with keys:
                - response: final text response from the agent
                - tool_calls: list of tools invoked with inputs/outputs
                - steps: number of LLM calls made
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        tool_calls_log = []
        steps = 0
        max_steps = 10  # Safety limit to prevent infinite loops
        retry_count = 0
        max_retries = 2  # Max retries per tool failure

        # Status descriptions for common tools
        tool_status_messages = {
            "get_high_value_customers": "🔍 Searching for high-value customers...",
            "get_customer_profile": "👤 Loading customer profile...",
            "search_customers": "🔎 Searching customer database...",
            "score_conversion_likelihood": "📊 Scoring conversion likelihood...",
            "recommend_products": "💡 Analyzing product recommendations...",
            "get_product_catalog": "📋 Loading product catalog...",
            "generate_whatsapp_message": "💬 Preparing personalized message context...",
        }

        if status_callback:
            status_callback("🧠 Analyzing your request...")

        while steps < max_steps:
            steps += 1

            if status_callback and steps > 1:
                status_callback(f"🔄 Reasoning step {steps}...")

            # Call LLM
            try:
                assistant_message = self._call_llm()
            except Exception as e:
                error_msg = str(e)
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    if status_callback:
                        status_callback("⏳ Rate limited — waiting 10 seconds...")
                    import time
                    time.sleep(10)
                    retry_count += 1
                    if retry_count <= max_retries:
                        steps -= 1  # Don't count this as a step
                        continue
                return {
                    "response": f"LLM API error: {error_msg}. Please try again.",
                    "tool_calls": tool_calls_log,
                    "steps": steps,
                }

            # Convert to dict for history
            msg_dict = {"role": "assistant", "content": assistant_message.content}

            # Check for tool calls
            if assistant_message.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ]
                self.conversation_history.append(msg_dict)

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    fn_name = tool_call.function.name

                    # Parse arguments safely
                    try:
                        fn_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        fn_args = {}
                        result = json.dumps({
                            "error": "Failed to parse tool arguments",
                            "raw_arguments": tool_call.function.arguments,
                            "suggestion": "Please provide valid JSON arguments."
                        })
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result,
                        })
                        continue

                    # Update status
                    if status_callback:
                        status_msg = tool_status_messages.get(
                            fn_name, f"⚙️ Running {fn_name}..."
                        )
                        status_callback(status_msg)

                    # Log the tool call
                    trace_entry = {
                        "step": steps,
                        "tool": fn_name,
                        "input": fn_args,
                    }

                    # Execute with validation
                    result = self._execute_tool(fn_name, fn_args)

                    # Check if tool returned an error
                    try:
                        result_parsed = json.loads(result)
                        if isinstance(result_parsed, dict) and "error" in result_parsed:
                            trace_entry["status"] = "error"
                            trace_entry["error"] = result_parsed["error"]
                            if status_callback:
                                status_callback(f"⚠️ Tool error: {result_parsed['error'][:50]}... Retrying...")
                        else:
                            trace_entry["status"] = "success"
                    except (json.JSONDecodeError, TypeError):
                        trace_entry["status"] = "success"

                    trace_entry["output_preview"] = result[:500] + ("..." if len(result) > 500 else "")

                    tool_calls_log.append(trace_entry)
                    self.execution_trace.append(trace_entry)

                    # Add tool result to conversation history
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

            else:
                # No tool calls – this is the final response
                self.conversation_history.append(msg_dict)

                if status_callback:
                    status_callback("✅ Composing final response...")

                break

        final_response = assistant_message.content or "I completed the analysis. Please see the tool results above."

        return {
            "response": final_response,
            "tool_calls": tool_calls_log,
            "steps": steps,
        }
