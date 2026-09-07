# Factory OS UI 设计评审稿 v0.2

完整的 69 项页面/动作统计、覆盖状态与新增设计板映射见：`Factory OS 页面与UI覆盖矩阵 v0.3.md`。

## 1. 设计结论

Factory OS 不应替换 Odoo WebClient，而应在 Odoo 19 的原生导航、Action、List、Form、Kanban、Search、Graph/Pivot、Chatter 与 Activity 体系内建立一层更轻、更聚焦的制造执行体验。

允许的重点定制：

- “今日工作台”使用一个专用 Owl Client Action，聚合异常、风险订单和今日任务。
- 销售订单增加独立的 Factory Execution State 与 Order Health，不修改 Odoo 原生交易状态。
- 表单内增加履约健康条、跨单据 Smart Buttons 和轻量履约链组件。
- 操作员、仓库、质检使用响应式专用动作页，但仍复用原生模型、权限、附件、Chatter 和 Activity。

不建议：

- 自建永久深色侧栏替代 Odoo Navbar/App Switcher。
- 在每个模块首页重复开发 KPI 驾驶舱。
- 将列表与详情长期锁定为自定义左右分栏，替代标准 List → Form 导航。
- 复制 Odoo 已有筛选、导入导出、附件、活动、消息、权限或状态能力。

## 2. 核心体验原则

1. 首页先回答“今天先处理什么”，KPI 放在最后。
2. 一个客户订单必须能串起物料、采购、生产、质量、交付与追溯。
3. Odoo 交易状态与 Factory OS 执行状态必须分开显示。
4. 桌面岗位使用标准 List/Form；现场岗位一屏完成一个动作。
5. 异常必须包含对象、原因、影响、负责人、截止时间和下一步。
6. 红黄绿只表达健康，不与业务阶段颜色混用。

## 3. 导航结构

Odoo 顶部 Navbar 展示 Factory OS 的主要应用入口；App Switcher 展示全部应用。根据角色隐藏无权访问的入口。

```text
今日工作台
订单
├ 客户
├ 报价单
└ 销售订单
产品与 BOM
├ 产品
├ BOM
└ 产品版本
采购
├ 供应商
├ 采购申请
└ 采购订单
库存
├ 库存
├ 收货
├ 领料/出库
├ 调拨
├ 批次
└ 盘点
生产
├ 生产订单
├ 工序
└ 今日生产任务
质量
├ 检验
├ NCR
└ 质量历史
交付
├ 待发货
├ 发货单
└ 交付历史
追溯
报表
设置
```

## 4. 完整页面清单

### P0 桌面端

| 领域 | 页面/视图 | 推荐 Odoo 载体 | 核心状态 |
|---|---|---|---|
| 今日工作台 | 异常、风险订单、今日节奏、次级 KPI | Owl Client Action | 正常、预警、风险 |
| 客户 | 列表、表单、订单 smart button | List + Form | 活跃、停用 |
| 产品 | 列表、表单、附件 | List + Form | 草稿、在产、停产 |
| BOM | 列表、表单、版本与组件行 | List + Form | 草稿、生效、失效 |
| 销售订单 | 列表、表单、履约总览 | List + Form | 交易状态 + 执行状态 + 健康状态 |
| 物料需求 | 缺料清单、订单需求明细 | List + Form | 齐套、部分缺料、缺料 |
| 供应商 | 列表、表单、采购与质量 smart button | List + Form | 活跃、停用 |
| 采购申请 | 列表、表单 | List + Form | 草稿、已批准、已转 PO、取消 |
| 采购订单 | 列表、表单、收货 smart button | List + Form | 草稿、确认、部分收货、已收货、延期、取消 |
| 库存 | 库存量、按库位/批次分组 | List + Search Panel | 正常、低库存、无库存 |
| 库存动作 | 收货、领料、调拨、调整、盘点 | List + Form | 草稿、就绪、完成、取消 |
| 批次 | 批次列表、表单、上下游追溯 | List + Form | 待检、合格、Hold、不合格 |
| 生产订单 | 列表、表单、工序与领料 smart button | List + Form | 草稿、物料就绪、待生产、生产中、质检、完成、三类 Hold、取消 |
| 工序 | 今日任务、工序记录 | Kanban/List + Form | 待开始、进行中、暂停、完成 |
| 检验 | 列表、检验表单、照片 | List + Form | 待检、进行中、PASS、FAIL、HOLD |
| NCR | Kanban、表单、整改验证 | Kanban + Form | Open、Containment、Root Cause、Corrective Action、Verification、Closed |
| 发货 | 待发货、发货单、POD | List + Form | Preparing、Ready、Shipped、Delivered |
| 追溯 | 正反向批次关系图与关联记录 | Owl Client Action + Forms | 链路完整、缺失记录、异常链路 |
| 报表 | 订单交付、生产、质量、库存、供应商 | Graph/Pivot/List | 只读聚合 |
| 设置 | 工厂、阈值、功能开关、角色、同步 | Settings Views | 系统配置 |

### P0 移动端

| 角色 | 页面 | 主动作 |
|---|---|---|
| 操作员 | 今日生产任务 | 开始工序 |
| 操作员 | 生产报工 | 确认完成/不良数量 |
| 操作员 | 报告异常 | 拍照并提交 |
| 仓库 | 今日仓库任务 | 选择收货/领料/调拨/盘点 |
| 仓库 | 扫码收货 | 确认数量、批次、库位 |
| 仓库 | 扫码领料 | 确认 MO、批次与数量 |
| 质检 | 待检任务 | 开始检验 |
| 质检 | 执行检验 | PASS/FAIL/HOLD，照片与备注 |
| 质检 | NCR 快速创建 | 隔离、责任人、截止日 |

## 5. 原 12 张图整改判断

| 原图 | 判断 | 主要原因与处理 |
|---|---|---|
| 01 核心模块首页 | 重做 | 欢迎图和模块入口重复 Odoo App Switcher；改为标准设置页、用户/权限页、产品/伙伴原生视图。 |
| 02 订单管理首页 | 大改 | 列表字段可保留；移除永久侧栏和常驻详情抽屉，改为 Odoo List → Form；补齐双状态与健康状态。 |
| 03 采购与库存首页 | 拆分重做 | 采购与仓库权限、动作不同；拆成两个应用菜单，缺料清单成为订单驱动入口。 |
| 04 生产管理首页 | 大改 | KPI/图表过多；主入口改为 MO List/Kanban 与今日工序，趋势放报表。 |
| 05 质量管理首页 | 大改 | 检验列表字段可用；详情回归 Form + Chatter，NCR 使用 Kanban 阶段。 |
| 06 交付管理首页 | 调整 | 数据结构基本可保留；详情改 Form，图片进入附件/Chatter，运输状态用 statusbar。 |
| 07 管理驾驶舱 | 必须重做 | 与 PRD 的异常优先顺序冲突；改为“今日工作台”基准图。 |
| 08 供应链协同首页 | 延后重做 | Connector 属于最后阶段；当前图暴露过多内部状态，需严格按共享字段与同步日志设计。 |
| 客户/供应商管理 | 调整 | 复用 res.partner List/Form；客户与供应商由菜单与搜索默认值区分，不创建平行 UI 框架。 |
| 产品管理 | 调整 | 列表字段与图片可保留；移除销售趋势和生命周期大盘，BOM/版本通过 smart button 与 notebook 进入。 |
| 报表中心 | 大改 | 删除“财务分析/毛利率”等超出 MVP 或需免责声明的主入口；复用 Graph/Pivot 与收藏筛选。 |
| 系统设置 | 重做 | 回归 Odoo res.config.settings、用户与访问权、技术设置；不把数据库维护伪装成普通业务设置。 |

## 6. 三张视觉基准

1. `Concepts/01-odoo-native-today-dashboard.png`：唯一允许强定制的桌面聚合主页。
2. `Concepts/02-odoo-native-order-form.png`：所有业务单据 Form View 的母版。
3. `Concepts/03-odoo-native-mobile-operations.png`：现场单动作移动页母版。

## 7. 第二批核心业务页面

4. `Concepts/04-odoo-native-material-shortage.png`：订单驱动的缺料处置，使用 Search Panel、分组 List 与 Odoo 记录活动；采购与库存保持分离。
5. `Concepts/05-odoo-native-inventory-lot.png`：以在手、预留、可用、在途、批次和库位为核心的库存真相页；库存价值不占据主工作面。
6. `Concepts/06-odoo-native-production-order.png`：标准 MO List/Form；正常生产阶段与异常 Hold/风险分开表达。
7. `Concepts/07-odoo-native-ncr.png`：NCR 使用原生 Kanban 阶段和 Form/Chatter 完成整改闭环。
8. `Concepts/08-odoo-native-delivery.png`：发货基于 `stock.picking` 扩展，以最终检验作为进入待发货的业务 Gate。
9. `Concepts/09-odoo-native-traceability.png`：唯一需要较强 Owl 定制的业务画布；节点仍打开原生表单，关联记录同时提供标准列表。

## 8. 第三批主数据、现场与配置页面

10. `Concepts/10-odoo-native-product-bom.png`：产品主数据与 BOM 版本；删除销售趋势、生命周期大盘与完整 PLM 流程。
11. `Concepts/11-odoo-native-purchase-order.png`：采购订单、ETA 变化、部分收货和受影响订单在原生 PO 表单内闭环。
12. `Concepts/12-odoo-native-inspection.png`：来料、过程和成品检验统一列表；单据流程状态与 PASS/FAIL/HOLD 结果分离。
13. `Concepts/13-odoo-native-mobile-warehouse.png`：仓库今日任务、扫码收货和生产领料三个移动端单动作工作面。
14. `Concepts/14-odoo-native-reports-v2.png`：只覆盖交付、生产、质量、库存和供应商五类 MVP 报表，复用 Dashboard/Graph/Pivot/List。v2 已修正顶部应用名称和导航文案漂移；旧稿不再作为基准。
15. `Concepts/15-odoo-native-settings.png`：历史设置探索稿，已被配置治理评审部分替代；其中全局批次追踪等表达不得实现。
16. `Concepts/25-odoo-native-setup-and-settings-v2.png`：历史配置导向向导稿；日常设置页风格仍可参考，但初始化问题不再作为基准。
17. `Concepts/25-odoo-native-progressive-setup-v3.png`：活动初始化基准。用订单看板、订单+进销存、标准生产、质量追溯四个 Quick Start preset 和六个现实问题生成原子配置；支持一人多岗，不保存管理等级。

## 9. Odoo 实现边界

优先 XML View Inheritance：字段、按钮、statusbar、smart buttons、groups、notebook、search filters、list decorations。

仅在以下位置使用 Owl：

- 今日工作台聚合与排序；
- 履约链/追溯关系可视化；
- 手机端扫码与大数字报工控件；
- 必要的跨模型健康状态组件。

不要修改 Odoo 原生 `sale.order.state` 表达制造执行；新增 `factory_execution_state`、`factory_health_state`、`factory_risk_code` 和 `factory_risk_message`。

定制等级：

| 等级 | 页面 | 实现边界 |
|---|---|---|
| 原生配置 | 客户、供应商、产品、BOM、采购订单、库存动作、检验、设置 | XML 视图继承、搜索视图、权限和原生字段组件 |
| 轻量增强 | 销售订单、缺料、库存批次、生产订单、NCR、发货 | 原生 List/Form/Kanban 加计算字段、smart button、alert 和小型状态组件 |
| 专用 Client Action | 今日工作台、全链路追溯 | Owl 负责聚合与关系呈现，记录操作仍通过 Odoo action/service 回到原生视图 |

## 10. 已锁定的跨模块规则

- `sale.order.state` 只表达销售交易生命周期；`factory_execution_state` 表达履约执行阶段。
- `factory_health_state` 只使用正常、预警、风险，不承担流程阶段语义。
- Hold 是异常状态或业务 Gate，不混入正常 statusbar 主路径。
- 所有异常统一包含对象、风险代码、通俗说明、影响、负责人、截止时间和下一步。
- Chatter 承担协作、附件、活动与审计可见性，不重复开发“动态日志”组件。
- 桌面使用 Odoo Search/List/Form/Kanban；移动端围绕扫码、数字、拍照和单一主动作。
- “不确定就配置”只适用于业务策略；系统正确性、安全和数据真实性不可配置。
- 批次/序列号追踪是产品级配置，不设置工厂级总开关。
- 设置页只使用有界枚举与明确依赖；所有配置变更必须审计。
- 首次安装使用六个现实问题和可选 Quick Start preset 生成推荐配置，日常修改仍进入 Odoo `res.config.settings`；preset 保存后不成为运行时状态。
- 正式 MRP 关闭时，订单仍可记录人工执行阶段、进度、预计完成、备注和附件，不生成 MO、物料需求或库存事务。
- Requested Delivery Date 可选；Committed Delivery Date 在订单进入活动执行前必须存在，Draft 可为 TBD。
- 非必要主数据使用 Just-in-Time Validation，不在首次建档时强制补齐。
- v0.1 不支持离线事务；网络失败只保留当前页面输入、显示未提交并允许手动重试，服务器确认前不得呈现成功。

配置目录、技术字段、依赖行为、渐进采用与不可变约束分别以 `docs/factory_os/configuration-matrix.md`、`configuration-schema.md`、`configuration-dependency-graph.md`、`progressive-adoption.md` 和 `system-invariants.md` 为准。

`Concepts/24-mobile-confirmation-and-offline-board.png` 为历史稿，包含错误的“本地保存/自动同步”表达，不得作为开发依据。活动基准为 `Concepts/24-mobile-confirmation-and-network-failure-v2.png`。

## 11. 页面覆盖状态

活动基准图已经覆盖：全局导航、今日工作台、订单、产品/BOM、采购缺料、采购订单、库存/批次、生产、检验、NCR、交付、追溯、报表、设置，以及操作员/质检/仓库移动端。初始化使用 25-v3，设置页结构沿用 25-v2 的右侧页面并受新 Schema 约束，网络失败使用 24-v2；15 与旧 24 均不属于活动基准。

客户与供应商不再单独创建强定制母版，直接复用 `res.partner` 的 List/Form/Contact/Chatter，通过默认搜索域、角色权限、smart buttons 和少量 Factory OS 字段区分。这部分沿用 `02-odoo-native-order-form.png` 的表单规范。

## 12. 下一轮确认点

- 顶部 Navbar 是否展示全部高频应用，还是只展示当前应用菜单。
- “采购”和“库存”是否确认拆成两个一级入口。
- 订单表单的履约链是默认展开，还是只在有风险时展开。
- 移动端第一批是否同时覆盖操作员、仓库、质检，还是先做操作员和质检。
