import json
from database.db import run_query


def get_high_value_customers(
    min_income: float = 500000,
    min_balance: float = 50000,
    min_credit_score: int = 650,
    segment: str = "",
    city: str = "",
    limit: int = 5,
) -> str:
    conditions = [
        "c.annual_income >= ?",
        "c.account_balance >= ?",
        "c.credit_score >= ?",
        "c.is_active = 1",
    ]
    params: list = [min_income, min_balance, min_credit_score]

    if segment:
        conditions.append("LOWER(c.segment) = LOWER(?)")
        params.append(segment)
    if city:
        conditions.append("LOWER(c.city) = LOWER(?)")
        params.append(city)

    where = " AND ".join(conditions)

    sql = f"""
    SELECT c.customer_id, c.first_name, c.last_name, c.age,
           c.city, c.occupation, c.annual_income, c.account_balance,
           c.credit_score, c.segment, c.relationship_vintage_years,
           c.phone
    FROM customers c
    WHERE {where}
    ORDER BY c.annual_income DESC
    LIMIT ?
    """
    params.append(limit)
    results = run_query(sql, tuple(params))
    return json.dumps(results, default=str)


def get_customer_profile(customer_id: str) -> str:
    customer = run_query(
        "SELECT customer_id, first_name, last_name, age, city, occupation, annual_income, account_balance, credit_score, segment, relationship_vintage_years, phone, email FROM customers WHERE customer_id = ?", (customer_id,)
    )
    if not customer:
        return json.dumps({"error": f"Customer {customer_id} not found"})

    profile = customer[0]

    products = run_query(
        """SELECT p.name, p.category, cp.status
           FROM customer_products cp
           JOIN products p ON cp.product_id = p.product_id
           WHERE cp.customer_id = ?""",
        (customer_id,),
    )
    profile["existing_products"] = products

    interactions = run_query(
        """SELECT interaction_type, summary, interaction_date
           FROM interaction_log
           WHERE customer_id = ?
           ORDER BY interaction_date DESC LIMIT 3""",
        (customer_id,),
    )
    profile["recent_interactions"] = interactions

    return json.dumps(profile, default=str)


def search_customers(query: str, limit: int = 5) -> str:
    sql = """
    SELECT customer_id, first_name, last_name, city, occupation,
           segment, annual_income, credit_score
    FROM customers
    WHERE (LOWER(first_name) LIKE LOWER(?) OR
           LOWER(last_name) LIKE LOWER(?) OR
           LOWER(city) LIKE LOWER(?) OR
           LOWER(occupation) LIKE LOWER(?) OR
           LOWER(segment) LIKE LOWER(?))
      AND is_active = 1
    ORDER BY annual_income DESC
    LIMIT ?
    """
    pattern = f"%{query}%"
    results = run_query(sql, (pattern, pattern, pattern, pattern, pattern, limit))
    return json.dumps(results, default=str)
