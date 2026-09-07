# Factory OS — Technical Risks（Phase 0 实测风险登记）

Date: 2026-09-07（Phase 0 r2）
来源：全部来自本 Phase 实测（native-behavior-audit / addon-dependency-map / security-baseline / state-map 的证据行）。每条含证据、影响、建议与责任 Phase。风险等级：P0（必须 Phase 1 前决策/缓解）、P1（Phase 1-3 内处理）、P2（观察项）。

## Gate Status（2026-09-07 Accepted closure）

```
Phase 0 evidence collection: complete
Phase 0 Gate: PASS — awaiting user authorization for Phase 1
闭环节点：ADR-006 = Accepted（Option 1 + amendments）；R1 架构冲突已裁决；
  R10 MTO 行为归 MRP Profile 受控能力；authority 文档一致；Test E–H 证据未变。
历史：r2 PASS → user STOP（BLOCKED, a19840b）→ ADR-006 Proposed →
  user Accept with amendments → 本 commit 收口为 PASS。
```

R1 由"未决架构冲突"转为 **已裁决**（ADR-006 Accepted）；残留执行风险转 Phase 1（单调校验/探测、orders 去 sale_stock、profile 安装）。不自动授权 Phase 1。

## P0

### R1 capability 分层 vs 原生引擎联动：已裁决（ADR-006 Accepted）→ 残留为 Phase 1 执行风险
- 证据：测试 A/B——只要 stock 已装，SO/PO 确认对任何 consu 货物（含非 storable plain）都生成 picking/move（A3R S00009/S00010、B P00001/P00002）；G——Safe Minimal（仅 sale，54 模块）下引擎模型全部不存在、Goods SO 确认零物流对象；H2/H3——同库渐进装 stock/mrp 后旧单零回溯、新单即入引擎。反向结论：**"已装引擎但 flag 关"不存在"回到无库存事务"的状态**。
- 裁决（2026-09-07）：**ADR-006 Accepted** = Option 1（Installed-addon profiles + monotonic upgrades）+ 强制修订——引擎型 capability（inventory/formal MRP，及进入 profile 的 purchasing/quality）单调、禁止假关闭；保持 8-addon（orders 去 sale_stock）；v0.1 purchasing→inventory；Profile 0–3 冻结；delivery 为业务层能力（不绑 Odoo delivery addon）；Business Preset ≠ Technical Installation Profile。受影响权威已同步（progressive-adoption v1.1 / configuration-schema / configuration-dependency-graph / 开发计划 / addon-dependency-map）。
- 残留执行风险（Phase 1）：profile→引擎安装映射与单调校验、"引擎在而 flag 关"一致性探测、orders manifest 去 sale_stock、supply 对 sale.order 的库存扩展、MTO 产品建模按 profile 校验（R10）。Phase 1 验收以 native-behavior-audit §8 E–H + harness 重跑为准。
- 责任：Phase 1（按 ADR-006 实现）；Phase 0 风险本身关闭。

### R10 原生 MTO：SO 确认自动建 MO/RFQ，flag 无法抑制（STOP B 补测结论）
- 证据：Test E（factory_phase0_mto）——激活 `stock.route_warehouse0_mto` + 产品 route=[Manufacture, MTO] + BoM，SO=S00002 确认即 **mo 0→1**（WH/MO/00001 confirmed, origin=S00002, qty=3.0），sale 行成品 move proc=make_to_order，`action_view_mrp_production()['res_id']==mo.id`；Test F——MTO+Buy+供应商 → SO 确认即 **po/rfq 0→1**（P00001 draft, origin=S00001）；H3 在同库渐进场景复现（mo 0→1）。配方对齐官方 sale_mrp 测试。
- 影响：原 Test C（is_mto=False）的「任何场景都不自动建 MO」过宽结论撤回；**MTO 配置 + 引擎已装时，`mrp_production_enabled=false` 无法阻止原生自动 MO/RFQ**——强化 R1 与 ADR-006；低能力级库若误配 MTO route 会绕过"无库存/MO 事务"承诺。
- 建议（ADR-006 Accepted 后）：MTO route 分配属 **MRP Profile 受控能力**（Profile 2，native-behavior-audit §0/§9）；产品建模/导入向导只在含 mrp 的 profile 库允许 MTO route，低能力级库阻止分配；orders 服务层对带 MTO 意图的 SO 行在低 profile 库校验（Phase 1 实现，验收 = Test E/H3 断言）。
- 责任：Phase 1（产品建模向导 + orders 校验 + profile 单调探测）。

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
- 证据：非 MTO 下 SO 确认不带 Manufacture 路线时无 MO（C1/C2）；orderpoint.action_replenish 仅返回向导动作、不直接产 MO/PO（C3：mo 0->0, po 3->3）。**MTO 例外**：MTO 激活 + 产品带 MTO route 时 SO 确认即自动 MO/RFQ（E/F/H3，见 R10），不受本条目"确认即 MRP"否定影响。
- 影响：factory_os_production 创建 MO 的路径必须是显式调用（直接建单或调度器环境补货），不能假设任何"确认即 MRP"——**除非产品走 MTO**（MTO 属原生自动，Factory OS 只需做 profile/校验）。
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
- Purchase-only（无 inventory 的采购模式）：ADR-006 **Accepted** 显式裁决 v0.1 不支持（purchasing requires inventory）；Odoo 的 purchase-without-stock 能力仅记录为原生现实，非漏项（Deferred/Post-MVP）。
- MO 非 MTO 下"确认不自动生成"**不是缺陷**：原生语义即"补货驱动"，与 ADR-003 设计一致；而 MTO 下"确认即自动 MO/RFQ"是原生正式行为（E/F/H3），属 MRP Profile 受控能力（R10/ADR-006），不是缺陷也不是可抑制的副作用。
