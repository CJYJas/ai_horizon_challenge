import os
import json
from typing import List
from backend.models import ExabytesProduct, GovernmentSupportModel, SupportingRules

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_exabytes_products() -> List[ExabytesProduct]:
    file_path = os.path.join(DATA_DIR, "exabytes_products.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [ExabytesProduct(**item) for item in data]

def load_government_support() -> List[GovernmentSupportModel]:
    file_path = os.path.join(DATA_DIR, "government_support.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [GovernmentSupportModel(**item) for item in data["government_support"]]

def load_supporting_rules() -> SupportingRules:
    file_path = os.path.join(DATA_DIR, "supporting_rules.json")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return SupportingRules(**data)
