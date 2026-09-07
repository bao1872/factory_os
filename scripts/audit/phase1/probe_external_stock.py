# -*- coding: utf-8 -*-
# Probe: stock installed externally, core present. Expect mismatch WITHOUT mutation.
service = env["factory.os.profile.service"]
company = env.company

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

check("stock installed", service._module_installed("stock"))
check("inventory flag false", company.factory_inventory_enabled is False,
      str(company.factory_inventory_enabled))

issues = service._consistency_issues(company)
codes = {i["code"] for i in issues}
check("issue STOCK_ENGINE_WITH_INVENTORY_OFF present",
      "STOCK_ENGINE_WITH_INVENTORY_OFF" in codes, str(codes))

# Prove no mutation: flag must remain False after detection.
check("inventory flag still false after detection",
      company.factory_inventory_enabled is False,
      str(company.factory_inventory_enabled))

for name, ok, detail in results:
    print(("PASS" if ok else "FAIL"), "|", name, ("" if ok else "| " + detail))

if not all(ok for _, ok, _ in results):
    raise SystemExit(1)
