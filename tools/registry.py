"""
Tool Registry – central registry of all tools with their OpenAI function-calling
schemas and references to the actual Python functions.
"""

from tools.customer_tools import get_high_value_customers, get_customer_profile, search_customers
from tools.scoring_tools import score_conversion_likelihood
from tools.product_tools import recommend_products, get_product_catalog
from tools.message_tools import generate_whatsapp_message

# ---------------------------------------------------------------------------
# OpenAI function-calling schemas
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_high_value_customers",
            "description": (
                "Retrieve high-value customers from the CRM database filtered by "
                "income, balance, credit score, segment, and city. Use this to find "
                "potential customers for outreach."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "min_income": {
                        "type": "number",
                        "description": "Minimum annual income filter (default 500000)",
                    },
                    "min_balance": {
                        "type": "number",
                        "description": "Minimum account balance filter (default 50000)",
                    },
                    "min_credit_score": {
                        "type": "integer",
                        "description": "Minimum credit score filter (default 650)",
                    },
                    "segment": {
                        "type": "string",
                        "description": "Customer segment filter: Retail, Premium, HNI, or Ultra-HNI",
                    },
                    "city": {
                        "type": "string",
                        "description": "City filter",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of customers to return (default 20)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_profile",
            "description": (
                "Get a detailed profile for a single customer including their "
                "existing products, recent interactions, and transaction summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer ID (e.g., CUST0001)",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_customers",
            "description": (
                "Search for customers by name, city, occupation, or segment. "
                "Supports partial text matching."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search text (name, city, occupation, or segment)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return (default 10)",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "score_conversion_likelihood",
            "description": (
                "Score a list of customers on their likelihood to convert for a "
                "specific product. Uses a heuristic model considering income, credit "
                "score, balance, transaction activity, relationship vintage, and "
                "existing products. Returns scored list sorted by likelihood."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_ids": {
                        "type": "string",
                        "description": "Comma-separated customer IDs to score (e.g., 'CUST0001,CUST0002,CUST0003')",
                    },
                    "product_type": {
                        "type": "string",
                        "description": "Product type to score for (e.g., 'Personal Loan', 'Credit Card', 'Mutual Fund SIP')",
                    },
                },
                "required": ["customer_ids", "product_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_products",
            "description": (
                "Recommend suitable bank products for a specific customer based on "
                "eligibility, portfolio gaps, and profile-based suitability analysis."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer ID to generate recommendations for",
                    },
                },
                "required": ["customer_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_catalog",
            "description": "Get the full bank product catalog with details and eligibility criteria.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_whatsapp_message",
            "description": (
                "Generate a personalized WhatsApp outreach message for a specific "
                "customer about a product. Includes personalization based on their "
                "profile, relationship history, and transaction patterns."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer ID",
                    },
                    "product_name": {
                        "type": "string",
                        "description": "Name of the product to pitch (e.g., 'Personal Loan')",
                    },
                    "tone": {
                        "type": "string",
                        "enum": ["professional", "friendly", "casual"],
                        "description": "Tone of the message (default: professional)",
                    },
                    "language": {
                        "type": "string",
                        "enum": ["English", "Hinglish"],
                        "description": "Language for the message (default: English)",
                    },
                    "include_offer": {
                        "type": "boolean",
                        "description": "Whether to include special offer details (default: true)",
                    },
                },
                "required": ["customer_id", "product_name"],
            },
        },
    },
]

# ---------------------------------------------------------------------------
# Map function names -> actual callables
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "get_high_value_customers": get_high_value_customers,
    "get_customer_profile": get_customer_profile,
    "search_customers": search_customers,
    "score_conversion_likelihood": score_conversion_likelihood,
    "recommend_products": recommend_products,
    "get_product_catalog": get_product_catalog,
    "generate_whatsapp_message": generate_whatsapp_message,
}
