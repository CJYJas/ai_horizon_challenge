import json

path = r'c:\Documents\Jasmine\ai_horizon_challenge\data\exabytes_products.json'
with open(path, 'r', encoding='utf-8') as f:
    products = json.load(f)

for p in products:
    cat = p.get("category", "").lower()
    ts = p.get("transformation_stage", "").lower()
    
    grant_cats = set(p.get("grant_categories", []))
    
    if ts == "digitalisation" or ts == "digitisation":
        grant_cats.add("digitalisation")
        grant_cats.add("technology_adoption")
    
    if cat in ["crm", "productivity", "cloud", "website", "other"]:
        grant_cats.add("software_adoption")
        
    if cat == "security":
        grant_cats.add("cybersecurity")
        grant_cats.add("technology_adoption")
        
    if cat == "cloud" or "aws" in p["name"].lower() or "cloud" in p["name"].lower():
        grant_cats.add("automation")
        
    if "ai" in p["name"].lower():
        grant_cats.add("innovation")
        
    p["grant_categories"] = list(grant_cats)

with open(path, 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=4)
print("Updated grant_categories")
