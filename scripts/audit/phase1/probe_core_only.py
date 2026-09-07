# -*- coding: utf-8 -*-
# Probe: core-only DB. Expect stock/mrp absent, flags false, no issues.
service = env["factory.os.profile.service"]
company = env.company

def inst(m):
    return service._module_installed(m)

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))

check("factory_os_core installed", inst("factory_os_core"))
check("stock not installed", not inst("stock"))
check("mrp not installed", not inst("mrp"))

check("inventory flag false", company.factory_inventory_enabled is False,
      str(company.factory_inventory_enabled))
check("mrp flag false", company.factory_mrp_production_enabled is False,
      str(company.factory_mrp_production_enabled))

issues = service._consistency_issues(company)
check("consistency issues empty", issues == [], str(issues))

for name, ok, detail in results:
    print(("PASS" if ok else "FAIL"), "|", name, ("" if ok else "| " + detail))

if not all(ok for _, ok, _ in results):
    raise SystemExit(1)
