# Phase 1A Disposable Integration Probes — factory_os_core

用途：在**一次性专用库**验证 `factory_os_core` 的引擎/能力一致性检测行为，证明「No Silent Reinterpretation」——引擎在而 flag 关时，只检测上报、不静默修复、不 mutate flag。

## 纪律（必须遵守）

- 只允许在一次性/专用审计库运行；禁止在任何工厂正式库执行。
- 每个 probe 以独立 `odoo shell` 会话运行，以 `env.cr.commit()` 结尾（脚本本身不 commit）。
- 输出重定向到 `/tmp`，不入库。
- 本目录只读取 registry/模型/flag 状态，**不修改任何 capability flag**。

## 环境前置

- venv python：`/Users/zhenbao/.workbuddy/binaries/python/envs/odoo19/bin/python`
- 引擎：`<repo>/odoo-19/odoo-bin`（Community 19.0）
- PostgreSQL：`/tmp:5432`，`--db_user=zhenbao`
- Factory OS addons：`<repo>/addons`

## 三个 DB 配方与预期

| probe | 初始化（-i） | 验证预期 |
|---|---|---|
| `probe_core_only.py` | `factory_os_core` | core installed；stock/mrp **未安装**；inventory/mrp flag=false；`_consistency_issues` == [] |
| `probe_external_stock.py` | `stock,factory_os_core` | stock installed；inventory flag=false；issue 含 `STOCK_ENGINE_WITH_INVENTORY_OFF` |
| `probe_external_mrp.py` | `mrp,factory_os_core` | mrp+stock installed；mrp/inventory flag=false；issue 含 `STOCK_ENGINE_WITH_INVENTORY_OFF` 与 `MRP_ENGINE_WITH_MRP_OFF` |

## 运行方式

```bash
cd <repo>
PYBIN=<venv python> ODOO_BIN=<repo>/odoo-19/odoo-bin

# 1. 建库并只装 core
$PYBIN $ODOO_BIN -d factory_phase1_core --addons-path=addons,odoo-19/odoo/addons \
    -i factory_os_core --stop-after-init --db_host=/tmp --db_user=zhenbao

# 2. 跑 core-only probe
{ cat scripts/audit/phase1/probe_core_only.py; echo; echo "env.cr.commit()"; } \
  | $PYBIN $ODOO_BIN shell -d factory_phase1_core \
      --addons-path=addons,odoo-19/odoo/addons --db_host=/tmp --db_user=zhenbao --no-http

# 3. 建库并装 stock + core（external-stock）
$PYBIN $ODOO_BIN -d factory_phase1_stock --addons-path=addons,odoo-19/odoo/addons \
    -i stock,factory_os_core --stop-after-init --db_host=/tmp --db_user=zhenbao
# 跑 probe_external_stock.py（同上 shell 方式）

# 4. 建库并装 mrp + core（external-mrp）
$PYBIN $ODOO_BIN -d factory_phase1_mrp --addons-path=addons,odoo-19/odoo/addons \
    -i mrp,factory_os_core --stop-after-init --db_host=/tmp --db_user=zhenbao
# 跑 probe_external_mrp.py（同上 shell 方式）
```

> `-i` 带逗号多模块在 Odoo 19 用逗号分隔即可（等价 `-i stock,factory_os_core`）。
