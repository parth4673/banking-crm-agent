"""
Product recommendation tools – match customers to suitable bank products
based on eligibility rules and their existing portfolio.
"""

import json
from database.db import run_query


def get_product_catalog() -> str:
    """Return the full product catalog with eligibility criteria."""
    products = run_query("SELECT * FROM products ORDER BY category, name")
    return json.dumps(products, indent=2, default=str)


def recommend_products(customer_id: str) -> str:
    """
    Recommend products for a specific customer based on:
      1. Eligibility (income and balance thresholds)
      2. Gap analysis (products they don't already have)
      3. Profile-based suitability scoring

    Returns a ranked list of recommended products with suitability reasons.
    """
    # Fetch customer
    custs = run_query("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    if not custs:
        return json.dumps({"error": f"Customer {customer_id} not found"})
    c = custs[0]

    # Existing active products
    existing = run_query(
        """SELECT p.product_id, p.name, p.category
           FROM customer_products cp JOIN products p ON cp.product_id = p.product_id
           WHERE cp.customer_id = ? AND cp.status = 'active'""",
        (customer_id,),
    )
    existing_ids = {e["product_id"] for e in existing}
    existing_categories = {e["category"] for e in existing}

    # All products
    products = run_query("SELECT * FROM products")

    recommendations = []

    for p in products:
        # Skip products customer already holds
        if p["product_id"] in existing_ids:
            continue

        # Check eligibility
        eligible = True
        reasons = []

        if c["annual_income"] < p["min_income"]:
            eligible = False
            reasons.append(f"Income ₹{c['annual_income']:,.0f} below minimum ₹{p['min_income']:,.0f}")

        if c["account_balance"] < p["min_balance"]:
            eligible = False
            reasons.append(f"Balance ₹{c['account_balance']:,.0f} below minimum ₹{p['min_balance']:,.0f}")

        if not eligible:
            continue

        # Suitability scoring
        suitability = 50  # base
        fit_reasons = []

        # Income headroom
        income_ratio = c["annual_income"] / max(p["min_income"], 1)
        if income_ratio >= 3:
            suitability += 20
            fit_reasons.append("Income well above threshold")
        elif income_ratio >= 1.5:
            suitability += 10
            fit_reasons.append("Income comfortably above threshold")

        # Credit score boost for loan products
        if p["category"] == "Loan" and c["credit_score"] >= 750:
            suitability += 15
            fit_reasons.append(f"Strong credit score ({c['credit_score']})")

        # Age-based suitability
        age = c.get("age", 30)
        if p["category"] == "Insurance" and 25 <= age <= 45:
            suitability += 10
            fit_reasons.append("Prime age for insurance")
        if p["category"] == "Investment" and 25 <= age <= 55:
            suitability += 10
            fit_reasons.append("Good age bracket for investments")
        if p["category"] == "Deposit" and age >= 45:
            suitability += 10
            fit_reasons.append("FD suitable for capital preservation")

        # Segment boost
        if c["segment"] in ("HNI", "Ultra-HNI") and p["category"] in ("Investment", "Insurance"):
            suitability += 10
            fit_reasons.append(f"{c['segment']} customer – wealth products fit well")

        # Gap fill bonus – if they don't have anything in this category
        if p["category"] not in existing_categories:
            suitability += 5
            fit_reasons.append(f"No existing {p['category']} products – portfolio gap")

        recommendations.append({
            "product_id": p["product_id"],
            "product_name": p["name"],
            "category": p["category"],
            "description": p["description"],
            "suitability_score": min(suitability, 100),
            "fit_reasons": fit_reasons,
        })

    # Sort by suitability
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)

    result = {
        "customer_id": customer_id,
        "customer_name": f"{c['first_name']} {c['last_name']}",
        "segment": c["segment"],
        "existing_products": [e["name"] for e in existing],
        "recommendations": recommendations[:5],  # Top 5
    }
    return json.dumps(result, indent=2, default=str)
