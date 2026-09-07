# Factory OS 页面与 UI 覆盖矩阵 v0.3

统计口径：一个独立菜单/Action 计为一个页面；同一 Form 的创建、编辑、只读状态不重复计数，但改变主要任务的动作页或移动端单动作状态单独计数。

## 汇总

| 范围 | 页面数 | 已有独立 UI | 已有母版但未独立落图 | 完全缺失 |
|---|---:|---:|---:|---:|
| 桌面业务页面 | 47 | 15 | 10 | 22 |
| 移动端动作页面 | 14 | 6 | 1 | 7 |
| 全局/系统页面 | 9 | 2 | 2 | 5 |
| 合计 | 70 | 23 | 13 | 34 |

说明：原始 12 张探索稿不计入“已有独立 UI”；当前只统计 `UI/Concepts` 中被确认或仍有效的 Odoo 原生设计稿。

**重要：70/70 只表示 Design Coverage，不等于 v0.1 Development Scope。** 开发以本文“开发范围矩阵”和“22 个 MVP 工作面”清单为准。

## 桌面页面清单

| # | 领域 | 页面 | Odoo 载体 | 状态 | 对应设计/缺口 |
|---:|---|---|---|---|---|
| 1 | 首页 | 今日工作台 | Owl Client Action | 已完成 | 01 |
| 2 | 首页 | 全部异常 | List/Form | 缺失 | 需独立异常队列与处置表单 |
| 3 | 订单 | 客户列表 | List/Kanban | 母版 | 原生 partner 列表未落图 |
| 4 | 订单 | 客户表单 | Form | 缺失 | 联系人、订单与交付 smart buttons |
| 5 | 订单 | 报价单列表 | List/Kanban | 缺失 | Odoo sale quotation |
| 6 | 订单 | 报价单表单 | Form | 缺失 | 报价转订单 |
| 7 | 订单 | 销售订单列表 | List | 母版 | 02 仅重点展示表单 |
| 8 | 订单 | 销售订单表单/履约总览 | Form | 已完成 | 02 |
| 9 | 产品 | 产品列表 | List/Kanban | 已完成 | 10 |
| 10 | 产品 | 产品表单 | Form | 已完成 | 10 |
| 11 | 产品 | BOM列表 | List | 母版 | 10 内嵌展示 |
| 12 | 产品 | BOM表单/版本 | Form | 已完成 | 10 |
| 13 | 产品 | 产品版本历史 | List/Form | 缺失 | 版本差异与生效期 |
| 14 | 采购 | 供应商列表 | List/Kanban | 母版 | partner 供应商域未落图 |
| 15 | 采购 | 供应商表单 | Form | 缺失 | 采购、到货、质量 smart buttons |
| 16 | 采购 | 缺料处置 | List/Form | 已完成 | 04 |
| 17 | 采购 | 采购申请列表 | List | 缺失 | 来源、审批、转PO |
| 18 | 采购 | 采购申请表单 | Form | 缺失 | Draft/Approved/Converted/Cancelled |
| 19 | 采购 | 采购订单列表 | List | 已完成 | 11 |
| 20 | 采购 | 采购订单表单 | Form | 已完成 | 11 |
| 21 | 库存 | 库存总览 | List/Search Panel | 已完成 | 05 |
| 22 | 库存 | 收货单 | List/Form | 缺失 | 桌面收货与来料检验 Gate |
| 23 | 库存 | 领料/出库单 | List/Form | 缺失 | MO 领料与部分领料 |
| 24 | 库存 | 调拨单 | List/Form | 缺失 | 源/目标库位与批次 |
| 25 | 库存 | 库存调整 | List/Form | 缺失 | 原因、前后值、审计 |
| 26 | 库存 | 盘点任务 | List/Form | 缺失 | 理论数、实盘数、差异 |
| 27 | 库存 | 批次列表/表单 | List/Form | 已完成 | 05 |
| 28 | 库存 | 低库存 | List | 母版 | 04/05 可复用但未独立落图 |
| 29 | 生产 | 生产订单列表/表单 | List/Form | 已完成 | 06 |
| 30 | 生产 | 工序列表 | List/Kanban | 母版 | 06 内嵌展示 |
| 31 | 生产 | 工序表单 | Form | 缺失 | 开始、暂停、报工、完成 |
| 32 | 生产 | 今日生产 | Kanban/List | 缺失 | 管理员桌面调度，不是移动报工 |
| 33 | 生产 | 生产异常 | List/Form | 缺失 | 缺料/停机/进度等统一记录 |
| 34 | 质量 | 检验单列表/表单 | List/Form | 已完成 | 12 |
| 35 | 质量 | NCR列表/表单 | Kanban/Form | 已完成 | 07 |
| 36 | 质量 | 质量历史 | List/Pivot | 缺失 | 产品/批次/供应商维度 |
| 37 | 交付 | 待发货 | List | 母版 | 08 可复用但未独立落图 |
| 38 | 交付 | 发货单列表/表单 | List/Form | 已完成 | 08 |
| 39 | 交付 | 交付历史 | List | 缺失 | Delivered/POD/实际交付日 |
| 40 | 追溯 | 全链路追溯 | Owl + List | 已完成 | 09 |
| 41 | 报表 | 订单交付 | Dashboard/Pivot | 已完成 | 14-v2 |
| 42 | 报表 | 生产分析 | Dashboard/Pivot | 缺失 | 计划、完成、不良、达成率 |
| 43 | 报表 | 质量分析 | Dashboard/Pivot | 缺失 | 合格率、不良率、NCR |
| 44 | 报表 | 库存分析 | Dashboard/Pivot | 缺失 | 低库存、呆滞、估算价值 |
| 45 | 报表 | 供应商分析 | Dashboard/Pivot | 缺失 | 准时率、周期、来料不良 |
| 46 | 设置 | 工厂OS设置 | Settings | 已完成 | 25 为活动基准；15 为历史稿 |
| 47 | 设置 | 用户与角色 | List/Form | 缺失 | 用户、角色、访问范围 |
| 47A | 设置 | 首次初始化向导 | Transient Model Wizard | 已完成 | 25-v3；现实问题与 Quick Start preset |

## 移动端动作页面

| # | 角色 | 页面/动作 | 状态 | 对应设计/缺口 |
|---:|---|---|---|---|
| 48 | 操作员 | 今日生产任务 | 已完成 | 03 |
| 49 | 操作员 | 生产报工 | 已完成 | 03 |
| 50 | 操作员 | 报告生产异常 | 缺失 | 类型、描述、照片、影响 |
| 51 | 操作员 | 工序完成确认 | 母版 | 03 需独立确认状态 |
| 52 | 仓库 | 今日仓库任务 | 已完成 | 13 |
| 53 | 仓库 | 扫码收货 | 已完成 | 13 |
| 54 | 仓库 | 生产领料 | 已完成 | 13 |
| 55 | 仓库 | 库存调拨 | 缺失 | 扫源/目标库位和批次 |
| 56 | 仓库 | 库存盘点 | 缺失 | 隐藏理论数模式与差异提交 |
| 57 | 仓库 | 库存调整 | 缺失 | 调整原因与审批提示 |
| 58 | 质检 | 待检任务 | 缺失 | 来料/过程/成品统一任务 |
| 59 | 质检 | 执行检验 | 已完成 | 03 |
| 60 | 质检 | NCR快速创建 | 缺失 | 隔离、责任人、截止日 |
| 61 | 通用 | 扫码结果/无结果 | 缺失 | 多对象匹配与错误态 |

## 全局与系统页面

| # | 页面 | 状态 | 缺口 |
|---:|---|---|---|
| 62 | 登录/数据库入口 | 母版 | 使用 Odoo 原生登录，需品牌化规范 |
| 63 | App Switcher/角色菜单 | 母版 | 01 已出现，需角色版本说明 |
| 64 | 全局搜索结果 | 缺失 | SO/PO/MO/Lot/NCR/Shipment 跨对象 |
| 65 | 通知中心 | 缺失 | 只展示高价值通知 |
| 66 | 我的活动 | 缺失 | Odoo Activity 聚合 |
| 67 | 附件查看/上传 | 母版 | 多表单已出现，需统一移动/桌面规则 |
| 68 | 审计日志 | 缺失 | Who/What/When/Before/After |
| 69 | 外部供应链协同 | 缺失 | 共享订单、同步日志、合作客户、数据权限、配置 |

## 剩余设计批次

1. 伙伴与销售：客户、供应商、报价单、订单列表。
2. 采购申请与库存动作：PR、收货、领料、调拨、调整、盘点。
3. 生产与质量补页：工序、今日生产、生产异常、质量历史。
4. 交付与分析：待发货、交付历史、四类剩余报表。
5. 全局与治理：搜索、通知、活动、审计、角色权限。
6. Connector：共享订单、同步日志、合作客户、数据权限、配置。
7. 移动端补页：异常、调拨、盘点、调整、待检、NCR、扫码错误态。

## 开发范围矩阵（Authority）

定义：`MVP-P0` 是首个端到端可运行闭环；`MVP-P1` 是 v0.1 验收前增强；`Post-MVP` 不进入 v0.1；`Native reuse only` 表示使用 Odoo 原生页面并仅做必要字段、域和权限扩展；`Deferred` 表示已有设计但不授权开发。

| # | Page | UI Coverage | Dev Priority | MVP Scope | Implementation Mode |
|---:|---|---|---|---|---|
| 1 | 今日工作台 | Done | MVP-P1 | Core surface 01 | Owl thin client action |
| 2 | 全部异常 | Designed | Post-MVP | Deferred | Native List/Form later |
| 3 | 客户列表 | Designed | MVP-P0 | Core surface 02 | Native reuse only |
| 4 | 客户表单 | Designed | MVP-P0 | Core surface 02 | Native reuse only + smart buttons |
| 5 | 报价单列表 | Designed | MVP-P1 | Core surface 03 | Native reuse only |
| 6 | 报价单表单 | Designed | MVP-P1 | Core surface 03 | Native reuse only |
| 7 | 销售订单列表 | Designed | MVP-P0 | Core surface 03 | Native + extend |
| 8 | 销售订单表单/履约总览 | Done | MVP-P0 | Core surface 03 | Native + extend |
| 9 | 产品列表 | Done | MVP-P0 | Core surface 04 | Native reuse only |
| 10 | 产品表单 | Done | MVP-P0 | Core surface 04 | Native + extend |
| 11 | BOM 列表 | Designed | MVP-P0 | Core surface 05 | Native reuse only |
| 12 | BOM 表单/版本 | Done | MVP-P0 | Core surface 05 | Native + thin version fields |
| 13 | 产品版本历史 | Designed | Post-MVP | Deferred | Native List/Form later |
| 14 | 供应商列表 | Designed | MVP-P0 | Core surface 06 | Native reuse only |
| 15 | 供应商表单 | Designed | MVP-P0 | Core surface 06 | Native reuse only + smart buttons |
| 16 | 缺料处置 | Done | MVP-P0 | Core surface 07 | Native List + computed risk |
| 17 | 采购申请列表 | Designed | Post-MVP | Deferred | Thin custom after MVP |
| 18 | 采购申请表单 | Designed | Post-MVP | Deferred | Thin custom after MVP |
| 19 | 采购订单列表 | Done | MVP-P0 | Core surface 08 | Native + extend |
| 20 | 采购订单表单 | Done | MVP-P0 | Core surface 08 | Native + extend |
| 21 | 库存总览 | Done | MVP-P0 | Core surface 09 | Native List/Search Panel |
| 22 | 收货单 | Designed | MVP-P0 | Core surface 10 | Native + QC gate extension |
| 23 | 领料/出库单 | Designed | MVP-P0 | Core surface 11 | Native reuse only |
| 24 | 调拨单 | Designed | Post-MVP | Deferred | Native reuse only later |
| 25 | 库存调整 | Designed | MVP-P1 | Core surface 09 | Native reuse + reason/audit |
| 26 | 盘点任务 | Designed | Post-MVP | Deferred | Native reuse only later |
| 27 | 批次列表/表单 | Done | MVP-P0 | Core surface 12 | Native reuse only |
| 28 | 低库存 | Designed | MVP-P1 | Core surface 07 | Native filtered action |
| 29 | 生产订单列表/表单 | Done | MVP-P0 | Core surface 13 | Native + extend |
| 30 | 工序列表 | Designed | MVP-P1 | Core surface 13 | Native reuse only |
| 31 | 工序表单 | Designed | MVP-P1 | Core surface 13 | Native + action guards |
| 32 | 今日生产 | Designed | Post-MVP | Deferred | Native action later |
| 33 | 生产异常 | Designed | MVP-P1 | Core surface 13 | Thin custom exception record |
| 34 | 检验单列表/表单 | Done | MVP-P0 | Core surface 14 | Native/thin quality model after audit |
| 35 | NCR 列表/表单 | Done | MVP-P0 | Core surface 15 | Thin custom Kanban/Form |
| 36 | 质量历史 | Designed | Post-MVP | Deferred | Native List/Pivot later |
| 37 | 待发货 | Designed | MVP-P0 | Core surface 16 | Native filtered picking action |
| 38 | 发货单列表/表单 | Done | MVP-P0 | Core surface 16 | Native + final gate extension |
| 39 | 交付历史 | Designed | MVP-P1 | Core surface 16 | Native filtered action |
| 40 | 全链路追溯 | Done | MVP-P1 | Core surface 17 | Owl read-only graph + native records |
| 41 | 订单交付报表 | Done | MVP-P1 | Core surface 22 | Native Graph/Pivot/Dashboard |
| 42 | 生产分析 | Designed | Post-MVP | Deferred | Native analytics later |
| 43 | 质量分析 | Designed | Post-MVP | Deferred | Native analytics later |
| 44 | 库存分析 | Designed | Post-MVP | Deferred | Native analytics later |
| 45 | 供应商分析 | Designed | Post-MVP | Deferred | Native analytics later |
| 46 | 工厂OS设置 | Done v2 | MVP-P0 | Core surface 18 | `res.config.settings` extension |
| 47 | 用户与角色 | Designed | MVP-P0 | Core surface 19 | Native reuse only + scoped fields |
| 47A | 首次初始化向导 | Done v3 | MVP-P0 | Core surface 20 | Transient Model Wizard; preset expands to atomic settings |
| 48 | 移动今日生产任务 | Done | MVP-P1 | Core surface 21 | Responsive native action |
| 49 | 移动生产报工 | Done | MVP-P1 | Core surface 21 | Thin mobile action |
| 50 | 移动报告生产异常 | Designed | MVP-P1 | Core surface 21 | Thin mobile action |
| 51 | 移动工序完成确认 | Designed | MVP-P1 | Core surface 21 | Thin confirmation state |
| 52 | 移动今日仓库任务 | Done | MVP-P1 | Core surface 10/11 | Responsive native action |
| 53 | 移动扫码收货 | Done | MVP-P1 | Core surface 10 | Thin mobile action |
| 54 | 移动生产领料 | Done | MVP-P1 | Core surface 11 | Thin mobile action |
| 55 | 移动库存调拨 | Designed | Post-MVP | Deferred | Native mobile later |
| 56 | 移动库存盘点 | Designed | Post-MVP | Deferred | Native mobile later |
| 57 | 移动库存调整 | Designed | Post-MVP | Deferred | Native mobile later |
| 58 | 移动待检任务 | Designed | MVP-P1 | Core surface 14 | Responsive native action |
| 59 | 移动执行检验 | Done | MVP-P1 | Core surface 14 | Thin mobile action |
| 60 | 移动 NCR 快速创建 | Designed | Post-MVP | Deferred | Thin mobile action later |
| 61 | 扫码结果/无结果 | Designed | MVP-P1 | Core surface 10/11/14 | Shared mobile state |
| 62 | 登录/数据库入口 | Designed | MVP-P0 | Platform | Native reuse only + brand |
| 63 | App Switcher/角色菜单 | Designed | MVP-P0 | Platform | Native reuse only |
| 64 | 全局搜索结果 | Designed | Post-MVP | Deferred | Deferred |
| 65 | 通知中心 | Designed | Post-MVP | Deferred | Use native Activity in MVP |
| 66 | 我的活动 | Designed | MVP-P1 | Platform | Native reuse only |
| 67 | 附件查看/上传 | Designed | MVP-P0 | Platform | Native reuse only |
| 68 | 审计日志 | Designed | MVP-P0 | Governance | Native mail tracking + thin audit view |
| 69 | 外部供应链协同 | Designed | Phase 8 | Deferred | Connector module, not v0.1 |

### 22 个 MVP 核心工作面

一个工作面可复用多个 Odoo List/Form/移动状态，因此不等同于页面行数：01 今日工作台；02 客户；03 报价/订单；04 产品；05 BOM；06 供应商；07 缺料/低库存；08 采购订单；09 库存总览/调整；10 收货；11 领料；12 批次；13 MO/工序/异常；14 检验；15 NCR；16 待发货/发货/交付历史；17 追溯；18 设置；19 用户与角色；20 初始化向导；21 移动生产/仓库/质检动作；22 订单交付报表。

其中 MVP-P0 先跑通主链与治理，MVP-P1 再补工作台、移动效率、追溯和基础报表。Post-MVP、Phase 8 和 Deferred 项即使已有设计，也不得自动进入 v0.1 开发。

## 补齐结果（2026-09-07）

当前设计板已把上表 70 个页面/动作全部映射到可见 UI。完成状态分为：

- 16 张独立高分辨率核心页面（15 为被替代历史稿，不计有效基准）；
- 10 张多页面设计板，共包含 35 个桌面/移动子页面及关键状态；
- 其余 20 项为同一页面的 List/Form、Tab 或 Odoo 标准状态变体，已在核心页或设计板中明确呈现，不另造重复页面。

新增设计板：

| 设计板 | 覆盖范围 |
|---|---|
| `16-partners-and-sales-board.png` | 客户列表、客户表单、供应商表单、报价单列表/表单 |
| `17-purchase-request-and-stock-actions-board.png` | 采购申请、收货、生产领料/调拨、盘点/调整 |
| `18-production-and-quality-board.png` | 今日生产、工序表单、生产异常、质量历史 |
| `19-delivery-and-reports-board.png` | 待发货、交付历史、生产分析、库存/供应商分析 |
| `20-global-governance-and-connector-board.png` | 全局搜索、通知/活动、审计日志、供应链协同 |
| `21-mobile-missing-actions-board.png` | 生产异常、移动调拨、盲盘、待检、NCR、扫码多结果与调整确认 |
| `22-secondary-master-data-and-access-board.png` | 产品版本、供应商列表、低库存、用户角色 |
| `23-login-attachments-and-sync-board.png` | 登录、角色应用菜单、附件、同步日志/数据权限 |
| `24-mobile-confirmation-and-offline-board.png` | 历史稿，不得实现本地草稿、自动同步或离线事务 |
| `24-mobile-confirmation-and-network-failure-v2.png` | 活动基准：工序完工、库存调整、检验确认、网络失败/手动重试 |
| `25-odoo-native-setup-and-settings-v2.png` | 历史配置导向向导；右侧日常设置风格可参考 |
| `25-odoo-native-progressive-setup-v3.png` | 活动基准：四个 Quick Start preset、六个现实问题、一人多岗 |

### 设计完成度说明

- 业务流程覆盖：70/70（新增首次初始化向导）。
- Odoo 载体定义：70/70。
- 独立高分辨率页面：16 个核心工作面（含替代设置基准）。
- 多页面板中的子页面：35 个。
- 标准 Odoo 复用变体：20 个。
- 尚未实现代码：全部；当前阶段是供确认的 UI 设计与页面规范。

### 开发前必须执行的视觉校正

多页面板用于确认信息结构和交互，不作为像素级实现截图。个别设计板的图像生成结果出现顶部导航字样、示例编号或日期轻微漂移；实现时必须以 01、02、04–14、24-v2、25 的白色 Odoo 原生 Navbar 和本文的准确页面名称为准，禁止照抄漂移文字。

初始化向导以 25-v3 为准；日常设置页沿用 Odoo `res.config.settings` 结构并以最新 Schema 为准。15 与 25-v2 的向导部分仅保留作历史对比。任何 C 类系统不变量不得因为旧图出现开关而进入开发。

网络失败实现以 `24-mobile-confirmation-and-network-failure-v2.png` 为准；文件名含 `offline-board` 的旧稿仅作历史对比。
