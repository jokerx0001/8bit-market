---
name: web2-dev:architecture
description: |
  架构设计 skill。被 orchestrator 在 plan 阶段调用。
  产出架构设计文档，合并了领域模型（实体关系、模块划分、数据流）。
  不包含实现细节——那是 design skill 的职责。

  <example>
  Context: new-orchestrator 阶段 4
  assistant: "使用 architecture skill 设计系统架构（含领域模型）。"
  </example>
---

# Architecture Design

产出架构设计文档。合并了领域模型分析。

## 数据来源

**必须读取以下文件：**
- `{task_dir}/.work/requirements.md` — 行为清单
- `{task_dir}/.work/user-prompt.md` — 用户原始输入
- `{task_dir}/.work/grill-interview.md` — grilling 采访记录
- 项目 CLAUDE.md — 技术约束、部署方式

## 产出

`{task_dir}/.work/architecture.md`，包含以下章节：

### 1. 模块划分

```markdown
## 模块划分

| 模块 | 职责 | 依赖 |
|------|------|------|
| user-service | 用户注册/登录/信息管理 | 无 |
| order-service | 订单创建/状态管理 | user-service, product-service |
| product-service | 商品 CRUD | 无 |
```

每个模块 = plan.md 中的一个任务。粒度控制在微服务/子模块级别。

### 2. 领域模型（实体关系）

```markdown
## 领域模型

### 实体
- User: id, email, password_hash, created_at
- Order: id, user_id, status, total_amount, created_at
- OrderItem: id, order_id, product_id, quantity, price

### 关系
User 1──N Order
Order 1──N OrderItem
OrderItem N──1 Product
```

### 3. 数据流

```markdown
## 数据流

用户注册: Client → API Gateway → user-service → DB
创建订单: Client → API Gateway → order-service → user-service(验证用户) → product-service(检查库存) → DB
```

### 4. 技术选型

```markdown
## 技术选型

- 后端框架: {从项目 CLAUDE.md 或技术栈检测}
- 数据库: {从项目 CLAUDE.md}
- 缓存: {从项目 CLAUDE.md}
- 前端框架: {从项目 CLAUDE.md}
```

## 约束

- 不包含实现代码
- 不包含 API 路由细节（那是 design skill 的职责）
- 模块粒度 = plan.md 任务粒度 = exec 循环粒度
- 领域模型包含实体定义 + 关系，不包含具体表结构（那是 design skill 的职责）
