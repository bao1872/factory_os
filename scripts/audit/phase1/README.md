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
| `probe_create_bypass.py` | `factory_os_core` | 尝试创建非法 company（Order Core off / MRP without inventory）→ 均 `ValidationError`；0 非法 company 残留 |

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

# 5. 建库并装 core（create-bypass）
$PYBIN $ODOO_BIN -d factory_phase1_create --addons-path=addons,odoo-19/odoo/addons \
    -i factory_os_core --stop-after-init --db_host=/tmp --db_user=zhenbao
# 跑 probe_create_bypass.py（同上 shell 方式）
```

> `-i` 带逗号多模块在 Odoo 19 用逗号分隔即可（等价 `-i stock,factory_os_core`）。

## Phase 1B 集成验证契约（强制，延后项）

### SETTINGS-AUDIT-01

```text
Owner: Phase 1B
Reason: core-only profile 有意不存在「既可写、又能通过模块/profile 校验
并成功生成 Settings 来源 audit row」的能力。这是 Safe Minimal 能力语义的
必然结果，非缺失实现的欠债。

Precondition:
已安装一个真实可写的 Factory OS workflow capability（其所属 addon/profile
已安装）。推荐首选：inventory profile（stock + factory_os_supply）已安装。

Action:
通过 res.config.settings 修改该 capability。

Required path:
res.config.settings
→ related inverse
→ res.company.write
→ factory.config.audit

Assertions:
audit row exists
source == "settings"
user_id == 实际用户
old_value/new_value 正确
一次真实变更恰好一条 row

禁止:
使用 factory_setup_complete（该字段在 res.config.settings 有意 readonly，
由 Setup Wizard / profile service 控制，非普通 Settings 开关）。
```
