# Factory OS 配置矩阵 v1.0

本文件是设置页、初始化向导、权限与自动化测试的共同基线。原则：业务差异可以配置；产品偏好提供默认值；系统正确性、安全和数据真实性不得配置。

## 分类与实现规则

| 类别 | 含义 | 实现方式 |
|---|---|---|
| A | 工厂之间确实不同的业务策略 | 有界配置项，显示依赖，变更留痕 |
| B | 产品推荐行为 | 提供合理默认值，允许授权角色覆盖 |
| C | 系统不变量 | 不出现在设置页，不提供关闭开关，以约束和测试保证 |

所有选择项必须是受控枚举，不提供自由输入状态机、规则表达式或“万能开关”。配置变更统一写入审计日志，至少记录操作者、时间、旧值、新值、作用域。

## 配置矩阵

| Setting | Class | Default | Scope | Editable role | Affects | Audited / dependency |
|---|---:|---|---|---|---|---|
| 工厂名称、Logo、地址、地区 | A | 初始化时填写 | Company | Factory OS Admin | 单据抬头、界面品牌、区域格式 | 是 |
| 时区、语言、币种 | A | Asia/Shanghai、简体中文、本位币 CNY | Company | Factory OS Admin | 日期、语言、金额 | 是；变更币种需遵循 Odoo 会计约束 |
| 重量、长度单位 | A | kg、mm | Company | Factory OS Admin | 产品、包装、物流 | 是 |
| 默认仓库 | A | 首个启用仓库 | Company | Factory OS Admin | 默认收发、生产位置 | 是；必须引用有效 `stock.warehouse` |
| 业务模块开关 | A | 销售、采购、库存、生产、质量、交付、报表启用；Connector 关闭 | Company | Factory OS Admin | 菜单、字段、流程 | 是；生产依赖库存与产品/BOM，质量 Gate 依赖质量模块 |
| 报价单 | B | 开启 | Company | Sales Manager | 报价到订单流程 | 是 |
| 客户要求日期 | C | 必填 | Order | 不可配置 | 履约承诺 | 由模型约束保证 |
| 客户确认日期 | C | 必填 | Order | 不可配置 | 排产与交付 | 由模型约束保证 |
| 计划完成日期显示 | B | 显示 | Company | Factory OS Admin | 订单、MO 页面 | 是 |
| 健康度预警/风险提前天数 | A | 7 天 / 3 天 | Company | Manager | 健康度计算 | 是；正常/预警/风险语义固定 |
| 履约链默认展示 | B | 仅风险时展开 | Company/User | Manager / User | 订单详情密度 | 是 |
| 采购申请模式 | A | 关闭 | Company | Purchase Manager | PR 菜单及审批 | 是；关闭/简易/需审批 |
| 采购审批 | A | 无审批 | Company | Purchase Manager | PO 确认 | 是；无/一人/指定角色，不支持多级自定义流 |
| PO 延期与 ETA 预警阈值 | A | 到期即延期；ETA 变化即提醒 | Company | Purchase Manager | 采购风险、通知 | 是 |
| 仓库与库位 | A | 一个默认仓库及标准库位 | Company/Warehouse | Inventory Manager | 库存动作 | Odoo 原生审计；不得创建虚假库存 |
| 产品追踪方式 | A | 不追踪 | Product | Product/Inventory Manager | 收货、领料、生产、追溯 | 是；不追踪/批次/序列号，不设全局追踪开关 |
| 来料质检 Gate | A | 关闭 | Company/Product | Quality Manager | 收货放行 | 是；启用质量模块后可用 |
| 最低库存、补货点、安全库存 | A | 空 | Product/Warehouse | Inventory Manager | 补货建议、缺料 | 是；产品/仓库级 |
| 盘点模式 | A | 普通盘点 | Company/Operation | Inventory Manager | 盘点录入 | 是；普通/盲盘 |
| 生产工序 | B | 开启 | Company | Production Manager | MO、工序、报工 | 是；关闭时隐藏工序级页面 |
| 报工模式 | A | 管理员与操作员 | Company | Production Manager | 报工入口 | 是；管理员/操作员/两者 |
| 条码要求 | A | 仓库和操作员可选 | Role | Factory OS Admin | 移动动作校验 | 是；必需/可选/不用 |
| 成品质检 Gate | B | 质量模块启用时开启 | Company | Quality Manager | Ready-to-Ship | 是；未通过不得进入待发货 |
| 不合格品处置 | A | 记录并影响库存状态 | Company | Quality Manager | 库存、报废、NCR | 是；仅记录/创建报废/阈值以上要求 NCR |
| 检验类型 | A | 来料、过程、成品启用 | Company | Quality Manager | 检验菜单与触发点 | 是；各自独立开关 |
| NCR 强制规则 | B | 高严重度或人工升级时强制 | Company | Quality Manager | 不合格闭环 | 是；每次失败/高严重度/人工升级 |
| 严重度阈值与显示名称 | A | Low/Medium/High/Critical | Company | Quality Manager | NCR 优先级、SLA | 是；四级语义固定，只可改阈值和显示名 |
| NCR SLA | A | 低 7天、中 5天、高 2天、关键 1天 | Company | Quality Manager | 活动截止、超期 | 是；按严重度 |
| 抽样数量 | A | 1 | Product/Inspection type | Quality Manager | 检验单 | 是；简单整数，不实现 AQL 引擎 |
| 包装信息 | A | 箱数、重量、CBM、照片启用 | Company | Delivery Manager | 发货准备 | 是；字段可分别启用 |
| 发货模式 | A | 国内与出口 | Company | Delivery Manager | 发货字段与单据 | 是；国内/出口/两者，条件显示 |
| 妥投确认 | A | 人工确认 | Company | Delivery Manager | Delivered 状态 | 是；人工/POD 必需/物流跟踪，MVP 实现前两项 |
| 移动作业台 | A | 仓库、操作员、质检启用 | Role | Factory OS Admin | 角色入口 | 是 |
| 操作员数据范围 | A | 自己 | Team/Role | Factory OS Admin | 工单、任务可见性 | 是；自己/班组/全部，仍受 record rule 约束 |
| 动作照片要求 | A | 异常和质检失败必需，其余可选 | Action type | Manager | 提交校验、附件 | 是；必需/可选/不用 |
| 通知类型、角色、提前天数 | A | 高价值风险通知；系统内 Activity | Company/Role | Manager | Activity/通知中心 | 是；MVP 不发外部消息 |
| 首页 KPI | B | 4 个核心 KPI | Role | Manager | 今日工作台 | 是；最多 6 个，不提供 BI 构建器 |
| 风险严重度映射 | A | 采用系统默认映射 | Company | Manager | 工作台排序、颜色 | 是；严重质检失败不可隐藏或降为正常 |
| 报表模块 | A | 只显示已启用业务模块 | Company/Role | Manager | 报表菜单 | 是；自动依赖模块开关 |
| 成本、售价、毛利可见性 | A | 仅授权经理 | Role | Factory OS Admin | 字段与报表 | 是；配置与访问组双重约束 |
| 内置角色与仓库/班组范围 | A | 预置最小角色集 | User | Factory OS Admin | ACL、record rules、菜单 | 是；只能分配角色与范围，不能编辑安全底线 |
| Connector 启用、端点、工作区、凭据 | A | 关闭 | Company | Integration Admin | 外部同步 | 是；凭据加密/受限显示 |
| Connector 允许共享字段 | A | 最小业务字段集，不含价格 | Company | Integration Admin | 同步载荷 | 是；价格可单独授权 |
| 私有数据禁止共享 | C | 永久禁止 | System | 不可配置 | Connector、导出 | 强制字段黑名单与测试 |
| 租户隔离 | C | 永久启用 | System | 不可配置 | 所有模型 | company/record rule/测试强制 |
| Odoo 原生交易状态语义 | C | 固定 | System | 不可配置 | sale/purchase/stock/mrp | 禁止用自定义状态覆盖原生状态 |
| 库存单一事实源 | C | `stock.*` | System | 不可配置 | 库存、追溯、报表 | 禁止平行库存台账 |
| 真实追溯来源 | C | `stock.move/lot` 与 `mrp` 关系 | System | 不可配置 | 正反向追溯 | 禁止手工伪造关系 |
| 健康度颜色语义 | C | 正常/预警/风险 | System | 不可配置 | 全局状态色 | 颜色和语义统一 |
| 配置与关键业务审计 | C | 永久启用 | System | 不可配置 | 治理 | 关键变更不可关闭 |

## 设置页信息架构

设置页沿用 Odoo `res.config.settings` 分组和原生控件，只保留可配置项：

1. 工厂
2. 订单
3. 采购
4. 库存
5. 生产
6. 质量
7. 交付
8. 通知
9. 用户与角色
10. 集成

C 类不变量不做开关；设置页底部只提供只读“系统保护已启用”摘要及文档入口。

## 初始化向导

首次安装只问六个高价值问题：工厂类型、启用模块、是否使用生产工序、是否有需要批次追踪的产品、是否启用成品质检 Gate、创建首批用户。向导据此生成推荐配置；产品追踪仍逐产品设置，向导只能帮助批量建立初始建议，不能创建全局追踪语义。
