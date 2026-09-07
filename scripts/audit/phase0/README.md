# Phase 0 Audit Harness — Odoo 19 Community native-behavior 复现

用途：**只读/审计工具，不包含任何 Factory OS 业务实现**。在 Odoo 升级后重跑 A–H，检测原生行为漂移（对版本契约测试，对应 native-behavior-audit.md 的 R3/R4 缓解）。

## 纪律（必须遵守）

- 只允许在**一次性/专用审计库**运行（脚本会创建并确认真实单据）；禁止在任何工厂正式库执行。
- 每个测试以独立 `odoo shell` 会话运行，并以 `env.cr.commit()` 结尾（脚本本身不 commit）。
- 输出重定向到 /tmp 等临时目录，**不入库**（转瞬即逝的 DB/输出文件保持 ignore）。
- 本目录不依赖、不修改 `odoo-19/` 引擎源码；只读取 registry/模型/行为。
- 每个测试脚本是自包含的（自行创建客户/产品/BOM/路线）；重复运行会产生递增序号单据，结论只读差量行。

## 环境前置

- venv python：`/Users/zhenbao/.workbuddy/binaries/python/envs/odoo19/bin/python`
- 引擎：`<repo>/odoo-19/odoo-bin`（Community 19.0，638 addons）
- PostgreSQL：`/tmp:5432`，`--db_user=zhenbao`

## 数据库配方（按测试所需原生安装面）

| DB profile | 初始化命令 | 适用测试 |
|---|---|---|
| Engine DB（72 模块：sale/stock/purchase/mrp 全引擎+桥接） | `python odoo-bin -d <db> --addons-path=addons,odoo/addons -i sale_management,stock,purchase,mrp --stop-after-init --db_host=/tmp --db_user=zhenbao` | `a1_simple_so` `a4_service_only` `b_purchase` `c1_manufacture_no_mto` `c3_orderpoint_replenish` `c4_mo_lifecycle` `d_later_enable` `e_mto_manufacture` `f_mto_buy` |
| Safe Minimal DB（54 模块，仅 sale） | `python odoo-bin -d <db> --addons-path=addons,odoo/addons -i sale --stop-after-init --db_host=/tmp --db_user=zhenbao` | `g_safe_minimal` `h1_old_so` |
| 渐进安装（H 系列，同一库分 3 步） | H1 后 `-i stock`（61 模块）→ `h2_stock_install_check` → `-i mrp`（64 模块）→ `h3_mrp_install_check` | h 系列 |

## 运行方式

```bash
cd <repo>
PYBIN=<venv python> ODOO_BIN=<repo>/odoo-19/odoo-bin \
  scripts/audit/phase0/run.sh factory_phase0_audit tests/a1_simple_so.py /tmp/phase0_audit
# 逐个脚本运行；H 系列须按 README 数据库配方在步骤间执行 odoo-bin -i
```

等价手动单测：

```bash
{ cat tests/e_mto_manufacture.py; echo; echo "env.cr.commit()"; } \
  | <venv python> odoo-bin shell -d <db> --addons-path=addons,odoo/addons \
      --db_host=/tmp --db_user=zhenbao --no-http > /tmp/phase0_audit/r2_test_e.txt 2>&1
```

## 测试清单与原始出处（provenance）

原始开发在 `/tmp/phase0_audit/`（临时，不入库）；收编改名如下。2026-09-07 全量在专用库验证（原始输出 `r2_*.txt` 记录于 native-behavior-audit.md §2/§8）。

| Harness 文件 | 源文件（/tmp/phase0_audit） | 验证库/证据章节 |
|---|---|---|
| tests/a1_simple_so.py | test_A_simple_so_r2.py | Engine DB · native-behavior-audit §2-A |
| tests/a4_service_only.py | test_A_service_only.py | 同上 · §2-A4 |
| tests/b_purchase.py | test_B_purchase.py | 同上 · §2-B |
| tests/c1_manufacture_no_mto.py | test_C_mrp.py | 同上 · §2-C |
| tests/c3_orderpoint_replenish.py | test_C3_mo_trigger.py | 同上 · §2-C3 |
| tests/c4_mo_lifecycle.py | test_C4_r2.py（含 done+Lot，取代 C4b） | 同上 · §2-C4R |
| tests/d_later_enable.py | test_D_later_enable.py | 同上 · §2-D |
| tests/e_mto_manufacture.py | test_E_mto_manufacture.py | factory_phase0_mto · §8-E |
| tests/f_mto_buy.py | test_F_mto_buy.py | factory_phase0_mto · §8-F |
| tests/g_safe_minimal.py | test_G_safe_minimal.py | factory_phase0_min · §8-G |
| tests/h1_old_so.py | test_H1_old_so.py | factory_phase0_min（54 模块）· §8-H |
| tests/h2_stock_install_check.py | test_H2_stock_install_check.py | 同上（61 模块，-i stock 后）· §8-H |
| tests/h3_mrp_install_check.py | test_H3_mrp_install_check.py | 同上（64 模块，-i mrp 后）· §8-H |
| probes/probe_native_acl.py | probe_native.py | ACL/字段探测 |
| probes/probe_record_rules.py | probe_rules.py | record rules/关键组探测 |

注：初版 `test_C4b_done.py`/`test_C4_mo_lifecycle.py`（17/18 API 崩溃版）已被 `c4_mo_lifecycle.py`（19 版，`lot_producing_ids` 复数）取代，不再收编。
