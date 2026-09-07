# Factory OS — Technical Risks（Phase 0 实测风险登记）

Date: 2026-09-07（Phase 0 r2）
来源：全部来自本 Phase 实测（native-behavior-audit / addon-dependency-map / security-baseline / state-map 的证据行）。每条含证据、影响、建议与责任 Phase。风险等级：P0（必须 Phase 1 前决策/缓解）、P1（Phase 1-3 内处理）、P2（观察项）。

## P0

### R1 能力分层 ≠ 原生联动：装了 stock/mrp 后原生规则不可由配置关闭
- 证据：测试 A/B——只要 stock 已装，SO/PO 确认对任何 consu 货物（含非 storable plain）都生成 picking/move（A3R S00009/S00010、B P00001/P00002）；Safe Minimal 下"无 BOM/库存/MO 的订单执行"只在**不装 stock**时成立。mrp 已装时仓库默认 Manufacture/Buy 路线存在（C_WH 实测）。
- 影响：configuration-schema 的 flags 只控 Factory OS UI/流程（开发计划 §0.1 L22）。若某工厂先装了 stock/mrp 而 inventory/mrp flag 关闭，原生仍会产 picking/可手动建 MO → "flag 关闭"≠"引擎停用"。
- 建议：**安装方案与能力分层绑定**（初始化向导按 Safe Minimal→Inventory→MRP→Quality 逐级安装模块，升级不可逆或记录迁移路径）；Factory OS 服务层在 flag 关闭时自校验（如拒绝展示原生库存菜单入口不等于安全——不变量 #8）；PRD/计划不含 stock 的简单执行闭环必须在**无 stock addon** 环境验证（Phase 2 Gate）。
- 责任：Phase 1（向导与安装矩阵）+ Phase 0 Gate 决策。

### R2 Community 无 quality addon → 质检与成品质检 Gate 全自建
- 证据：addon 目录与 registry 均无 quality.check/point/alert（EXIST=False）；无 enterprise。
- 影响：不变量 #5（失败数量必须受控处置）、#6（成品质检 Gate）、#11（Gate 依赖质量模块）的"模块"语义无原生实现；PRD §36 复用清单中的 quality.* 落空。
- 建议：按开发计划 §20「无 Quality」路径冻结两个薄模型（factory.quality.inspection/ncr，已入 model-mapping #14/#15）；Phase 5 前完成 FAIL→isolation/scrap/return 处置与 READY_TO_SHIP Gate 服务校验；**禁止**为"省事"引入 record_only 处置（不变量 #5）。
- 责任：Phase 5；Phase 1 需在 core 预留 audit/处置服务接口。

### R3 19 版型差异已被实测锁定，历史记忆/外部资料不可再作依据
- 证据：type 枚举无 'product'（改 is_storable）；procurement.group 移除；stock.move 无 name/quantity_done；stock.move.line 无 product_uom_qty/qty_done（用 quantity）；mrp.production 无单数 lot_producing_id（复数 M2M）；button_mark_done 存在（mrp_production.py:2219）；无持久 stock.inventory/count。
- 影响：任何按 17/18 文档或旧记忆编写的代码/脚本/导入都会崩（本 Phase 初版测试已踩 5 处）。
- 建议：本 Phase 6 份输出作为唯一版本事实基线；新增字段引用前先 `_fields` 探测；升级 Odoo minor 版本需重跑强制测试 A-D。
- 责任：全部 Phase。

## P1

### R4 原生自动补货触发入口与旧 procurement API 差异
- 证据：SO 确认不带 Manufacture 路线时无 MO（C1/C2）；orderpoint.action_replenish 仅返回向导动作、不直接产 MO/PO（C3：mo 0->0, po 3->3）。
- 影响：factory_os_production 创建 MO 的路径必须是显式调用（直接建单或调度器环境补货），不能假设任何"确认即 MRP"。
- 建议：Phase 3 先补"调度器触发补货→MO/组件采购"端到端测试（本 Phase §7 补测项 1），据此设计 factory_os_supply 的缺料服务与操作入口。
- 责任：Phase 3。

### R5 原生默认权限宽于 Factory OS 安全底线
- 证据：security-baseline——采购/库存/生产/产品 record rule 仅 multi-company（无个人/班组范围）；sale.order.line 等含价格字段对 Sales/User 可写；product.template 业务域只读而创建组单一；stock.move.line 全员可写、stock.quant 全员只读。
- 影响：操作员默认可见全公司订单/库存（记录级）与报价/成本类字段（字段级），不满足不变量 #8 默认要求。
- 建议：Phase 1 建工厂OS角色组 + record rules + 字段 groups；Operator 越权测试（开发计划 §41）用本基线做差分；禁止菜单隐藏代替授权。
- 责任：Phase 1。

### R6 plain（非 storable）goods 也被 picking/move 追踪
- 证据：A3R S00010、B P00002——consu+is_storable=False 的货物在 SO/PO 确认时仍生成完整 delivery/incoming picking + move。
- 影响：工厂OS若以"非 storable = 不需要库存管理"做分类假设会出错；这些货仍走 wh 默认路线。
- 建议：产品建模向导明确三分类（service / storable goods / non-storable goods），并对 non-storable goods 说明"装 stock 后仍有 picking 流程"；导入模板校验 type+is_storable 组合。
- 责任：Phase 1（core 产品扩展）+ 数据导入。

### R7 基础安装会带入大量附加模块（攻击面/维护面）
- 证据：仅以 sale_management,stock,purchase,mrp 起步，自动安装 72 模块（含 account/account_edi、spreadsheet*、iap/mail 相关、auth_totp/passkey、digest/sms/snailmail 等）。
- 影响：默认权限面、后台任务与升级面变大；其中部分模块带外部服务（iap/partner_autocomplete/snailmail/google_gmail）。
- 建议：正式工厂模板在 Phase 1 明确最小模块清单（可能另建精简初始化）；生产部署关闭无关外部服务、按最小权限配邮件/门户；审计 auth 模块启用情况。
- 责任：Phase 1 + 部署检查清单。

## P2

### R8 桥接模块自动启用影响预期
- 证据：安装集自动含 sale_mrp/sale_purchase/purchase_mrp/stock_account/mrp_account（addon-dependency-map §4）。
- 影响：sale+mrp 同装即具备 sale→mfg 联动；stock_account 引入会计口径库存金额（只读给 Invoicing/Accounting 组）。
- 建议：Phase 3/6 复核这些桥接对"简单订单执行 + 库存金额只读"的影响；若某工厂出现库存金额需求属 accounting guardrail（PRD §34 明确 MVP 禁 Accounting），注意 stock_account 已带入基本 valuation。
- 责任：Phase 3/6 观察。

### R9 Community/Enterprise 双轨
- 影响：若未来某工厂用 Enterprise，quality.*/更完整 MRP 排程出现，model-mapping 与 addon-dependency-map 需出 Enterprise 映射版本。
- 建议：保持 factory addon 不写死 Enterprise 依赖；加版本化映射注释。
- 责任：架构长期观察（本 Phase 冻结 Community）。

## 已排除/非风险（证据边界）

- 平行库存/平行生产：已被 system-invariants #3 + ADR-002/003 排除，Phase 0 不重开（ADR-002 Supersedes）。
- 离线事务：ADR-005 排除，本 Phase 未测试（不适用于 v0.1）。
- MO 自动生成缺失**不是缺陷**：原生语义即"补货驱动"，与 ADR-003 设计一致（见 native-behavior-audit §3.1）。
