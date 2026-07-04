"""
Scoring tools – estimate how likely a customer is to convert for a given product.

Uses a rules-based heuristic model. Each factor contributes points to a 0-100 score.
This is transparent and explainable, which matters in banking.
"""

import json
from database.db import run_query


def _has_product(customer_id: str, product_category: str) -> bool:
    """Check if customer already has an active product in this category."""
    rows = run_query(
        """SELECT 1 FROM customer_products cp
           JOIN products p ON cp.product_id = p.product_id
           WHERE cp.customer_id = ? AND LOWER(p.category) = LOWER(?)
             AND cp.status = 'active'
           LIMIT 1""",
        (customer_id, product_category),
    )
    return len(rows) > 0


def _get_txn_stats(customer_id: str) -> dict:
    """Get transaction stats for scoring."""
    rows = run_query(
        """SELECT
             COUNT(*) as txn_count,
             COALESCE(SUM(CASE WHEN txn_type='debit' THEN amount ELSE 0 END), 0) as total_debits,
             COALESCE(SUM(CASE WHEN txn_type='credit' THEN amount ELSE 0 END), 0) as total_credits,
             COALESCE(SUM(CASE WHEN category='EMI Payment' THEN 1 ELSE 0 END), 0) as emi_count
           FROM transactions WHERE customer_id = ?""",
        (customer_id,),
    )
    return rows[0] if rows else {}


def score_conversion_likelihood(customer_ids: str, product_type: str = "Personal Loan") -> str:
    """
    Score a list of customers (comma-separated IDs) on their likelihood
    to convert for a given product type. Returns scored list sorted by
    likelihood (highest first) with explanations for each score.

    Scoring factors (0-100 scale):
      - Income adequacy (0-20 points)
      - Credit score health (0-20 points)
      - Account balance (0-15 points)
      - Transaction activity (0-15 points)
      - Relationship vintage (0-10 points)
      - No existing similar product (0-10 points)
      - Spending pattern signals (0-10 points)
    """
    ids = [cid.strip() for cid in customer_ids.split(",")]

    # Fetch customer data
    placeholders = ",".join(["?"] * len(ids))
    customers = run_query(
        f"SELECT * FROM customers WHERE customer_id IN ({placeholders})",
        tuple(ids),
    )

    product_type_lower = product_type.lower()

    # Determine product category for overlap check
    category_map = {
        "personal loan": "Loan",
        "home loan": "Loan",
        "business loan": "Loan",
        "gold loan": "Loan",
        "credit card": "Card",
        "premium credit card": "Card",
        "fixed deposit": "Deposit",
        "mutual fund sip": "Investment",
        "term life insurance": "Insurance",
    }
    product_category = category_map.get(product_type_lower, "Loan")

    scored = []

    for c in customers:
        score = 0
        reasons = []

        # 1. Income adequacy (0-20)
        income = c.get("annual_income", 0)
        if income >= 1500000:
            score += 20
            reasons.append("High income (20pts)")
        elif income >= 800000:
            score += 15
            reasons.append("Good income (15pts)")
        elif income >= 400000:
            score += 10
            reasons.append("Moderate income (10pts)")
        else:
            score += 3
            reasons.append("Low income (3pts)")

        # 2. Credit score (0-20)
        cs = c.get("credit_score", 0)
        if cs >= 800:
            score += 20
            reasons.append(f"Excellent credit score {cs} (20pts)")
        elif cs >= 720:
            score += 16
            reasons.append(f"Good credit score {cs} (16pts)")
        elif cs >= 650:
            score += 10
            reasons.append(f"Fair credit score {cs} (10pts)")
        else:
            score += 3
            reasons.append(f"Low credit score {cs} (3pts)")

        # 3. Account balance (0-15)
        balance = c.get("account_balance", 0)
        if balance >= 500000:
            score += 15
            reasons.append("Strong account balance (15pts)")
        elif balance >= 200000:
            score += 10
            reasons.append("Decent account balance (10pts)")
        elif balance >= 50000:
            score += 5
            reasons.append("Moderate account balance (5pts)")

        # 4. Transaction activity (0-15)
        txn_stats = _get_txn_stats(c["customer_id"])
        txn_count = txn_stats.get("txn_count", 0)
        if txn_count >= 30:
            score += 15
            reasons.append(f"Very active ({txn_count} txns, 15pts)")
        elif txn_count >= 20:
            score += 10
            reasons.append(f"Active ({txn_count} txns, 10pts)")
        elif txn_count >= 10:
            score += 5
            reasons.append(f"Moderately active ({txn_count} txns, 5pts)")

        # 5. Relationship vintage (0-10)
        vintage = c.get("relationship_vintage_years", 0)
        if vintage >= 5:
            score += 10
            reasons.append(f"Long relationship ({vintage}yrs, 10pts)")
        elif vintage >= 2:
            score += 6
            reasons.append(f"Established relationship ({vintage}yrs, 6pts)")
        else:
            score += 2
            reasons.append(f"New relationship ({vintage}yrs, 2pts)")

        # 6. No existing similar product (0-10)
        cid = c["customer_id"]
        if not _has_product(cid, product_category):
            score += 10
            reasons.append(f"No existing {product_category} product (10pts)")
        else:
            reasons.append(f"Already has {product_category} product (0pts)")

        # 7. Spending pattern signals (0-10)
        emi_count = txn_stats.get("emi_count", 0)
        total_debits = txn_stats.get("total_debits", 0)
        total_credits = txn_stats.get("total_credits", 0)

        if product_type_lower in ("personal loan", "home loan", "business loan"):
            # High spending with manageable EMIs = good candidate
            if total_debits > 0 and emi_count <= 3 and total_credits > total_debits:
                score += 10
                reasons.append("Healthy cashflow with low EMI burden (10pts)")
            elif total_credits > total_debits:
                score += 5
                reasons.append("Positive cashflow (5pts)")
        elif product_type_lower in ("mutual fund sip", "fixed deposit"):
            if total_credits > total_debits * 1.5:
                score += 10
                reasons.append("Surplus cashflow – good for investment (10pts)")

        # Determine tier
        if score >= 75:
            tier = "HOT"
        elif score >= 55:
            tier = "WARM"
        elif score >= 35:
            tier = "MILD"
        else:
            tier = "COLD"

        scored.append({
            "customer_id": cid,
            "customer_name": f"{c['first_name']} {c['last_name']}",
            "score": score,
            "tier": tier,
            "product": product_type,
            "reasons": reasons,
        })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)
    return json.dumps(scored, indent=2)
