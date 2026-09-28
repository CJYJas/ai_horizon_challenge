import json
import os

path = r'c:\Documents\Jasmine\ai_horizon_challenge\data\exabytes_products.json'
with open(path, 'r', encoding='utf-8') as f:
    products = json.load(f)

# Hardcoded mapping of product_id to evidence_signals based on problems_solved/benefits
signals_map = {
    "freshsales": ["customer information stored in spreadsheets", "manual customer follow-up", "no centralized customer database", "manual reporting", "leads are difficult to track"],
    "microsoft_365": ["fragmented productivity tools", "need cloud-based document access", "manual remote collaboration"],
    "google_workspace": ["fragmented collaboration tools", "need shared cloud documents", "need professional email", "manual remote collaboration"],
    "lark": ["team communication is fragmented", "switch between multiple applications", "rely on manual workflows", "approvals are inefficient"],
    "ai_web_hosting": ["does not have a website", "lacks technical expertise to build a website", "website is difficult to manage"],
    "freshdesk": ["customer enquiries are difficult to manage", "customer support is fragmented", "manual issue tracking"],
    "freshchat": ["website visitors cannot easily contact", "customer conversations are fragmented", "manual digital customer engagement"],
    "ecommerce_design": ["wants to start selling online", "lacks an ecommerce website", "manual online sales tracking"],
    "bulk_sms": ["customer outreach is inefficient", "manual promotional messaging"],
    "email_marketing": ["struggles to maintain customer engagement", "customer outreach is inconsistent"],
    "ecloudapp": ["business needs cloud-based business applications", "inaccessible applications across devices"],
    "acronis_cyberprotect": ["business needs data backup", "manual data protection"],
}

added_signals = {}

for p in products:
    pid = p["product_id"]
    if pid in signals_map:
        p["evidence_signals"] = signals_map[pid]
        added_signals[pid] = signals_map[pid]
    else:
        # Generate some generic ones from problems_solved
        ps = [prob.lower() for prob in p.get("problems_solved", [])]
        signals = [prob for prob in ps if "manual" in prob or "fragmented" in prob or "difficult" in prob or "poorly" in prob or "inefficient" in prob]
        if not signals:
            signals = [ps[0]] if ps else []
        p["evidence_signals"] = signals
        added_signals[pid] = signals

with open(path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4)

print("Updated exabytes_products.json successfully.")
print("Added signals:")
for k, v in added_signals.items():
    print(f"{k}: {v}")
