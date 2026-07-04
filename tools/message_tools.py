import json
from database.db import run_query


def generate_whatsapp_message(
    customer_id: str,
    product_name: str,
    tone: str = "professional",
    language: str = "English",
    include_offer: bool = True,
) -> str:
    if not customer_id or not customer_id.strip():
        return json.dumps({"error": "customer_id is required"})
    if not product_name or not product_name.strip():
        return json.dumps({"error": "product_name is required"})

    custs = run_query("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    if not custs:
        return json.dumps({"error": f"Customer {customer_id} not found"})
    c = custs[0]

    existing = run_query(
        """SELECT p.name FROM customer_products cp
           JOIN products p ON cp.product_id = p.product_id
           WHERE cp.customer_id = ? AND cp.status = 'active'""",
        (customer_id,),
    )
    existing_names = [e["name"] for e in existing]

    name = c["first_name"]
    vintage = c["relationship_vintage_years"]
    city = c["city"]
    occupation = c["occupation"]
    segment = c["segment"]

    # Greeting
    if tone == "casual":
        greeting = f"Hi {name}! 👋"
    elif tone == "friendly":
        greeting = f"Hello {name}! 😊"
    else:
        greeting = f"Dear {name},"

    # Relationship acknowledgement
    if vintage >= 5:
        relation = f"Thank you for being a valued customer for over {int(vintage)} years!"
    elif vintage >= 2:
        relation = f"We appreciate your {vintage}-year relationship with us."
    else:
        relation = "We hope you're enjoying our banking services."

    # Occupation-based personalization
    occ_line = ""
    if "doctor" in occupation.lower() or "medical" in occupation.lower():
        occ_line = "As a medical professional, we understand your unique financial needs. "
    elif "engineer" in occupation.lower() or "software" in occupation.lower():
        occ_line = "As a tech professional, you deserve smart financial solutions. "
    elif "business" in occupation.lower():
        occ_line = "As a business owner, we know growth needs the right financial backing. "
    elif "ca" in occupation.lower() or "chartered" in occupation.lower():
        occ_line = "As a finance professional, you'll appreciate the value in this. "

    # Product-specific offer
    if "loan" in product_name.lower():
        offer = "✅ Competitive interest rates\n✅ Quick approval in 24hrs\n✅ Minimal documentation"
    elif "credit card" in product_name.lower():
        offer = "✅ Airport lounge access\n✅ 5X reward points\n✅ Zero joining fee"
    elif "insurance" in product_name.lower():
        offer = "✅ Lowest premiums this quarter\n✅ Tax benefits under 80C\n✅ Instant policy issuance"
    elif "mutual fund" in product_name.lower() or "sip" in product_name.lower():
        offer = "✅ Curated fund selection\n✅ Start with just ₹500/month\n✅ Auto-debit facility"
    else:
        offer = "✅ Competitive returns\n✅ Flexible options\n✅ Priority processing"

    offer_section = f"\n🎯 *Special offer this month:*\n{offer}\n" if include_offer else ""

    existing_note = ""
    if existing_names:
        existing_note = f"\nAs a {segment} customer already using {existing_names[0]}, you get priority processing. "

    message = f"""{greeting}

{relation}

{occ_line}Based on your profile, we'd like to introduce our *{product_name}* — tailored for customers like you in {city}.{existing_note}
{offer_section}
Would you like to learn more? Just reply here or call me anytime! 📞

Warm regards,
Your Relationship Manager 🏦"""

    return json.dumps({
        "customer_id": customer_id,
        "customer_name": f"{c['first_name']} {c['last_name']}",
        "product": product_name,
        "phone": c["phone"],
        "generated_message": message,
    }, default=str)
