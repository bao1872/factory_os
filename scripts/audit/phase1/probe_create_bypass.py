# -*- coding: utf-8 -*-
# Probe: create() invariant bypass. Attempt invalid company creation and
# assert ValidationError + zero invalid companies remain.
from odoo.exceptions import ValidationError

Company = env["res.company"]
results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

base_count = Company.search_count([])

# 1. Order Core disabled.
try:
    Company.create({
        "name": "INVALID ORDER CORE",
        "factory_sales_enabled": False,
    })
    check("create rejects disabled order core", False, "no error raised")
except ValidationError:
    check("create rejects disabled order core", True)

# 2. MRP enabled without inventory.
try:
    Company.create({
        "name": "INVALID MRP",
        "factory_inventory_enabled": False,
        "factory_mrp_production_enabled": True,
    })
    check("create rejects mrp without inventory", False, "no error raised")
except ValidationError:
    check("create rejects mrp without inventory", True)

after_count = Company.search_count([])
check("no invalid companies remain", after_count == base_count,
      f"before={base_count} after={after_count}")

for name, ok, detail in results:
    print(("PASS" if ok else "FAIL"), "|", name, ("" if ok else "| " + detail))

if not all(ok for _, ok, _ in results):
    raise SystemExit(1)
