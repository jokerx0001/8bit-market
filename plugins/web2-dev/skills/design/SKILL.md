---
name: web2-dev:design
description: |
  详细设计 skill。被 orchestrator 在 plan 阶段调用。
  按模块组织，产出：数据库设计、API 接口设计、模块间交互。
  这是 exec 阶段 coding agent 的主要参考文档。

  <example>
  Context: new-orchestrator 阶段 5
  assistant: "使用 design skill 编写详细设计（按模块：DB + API + 交互）。"
  </example>
---

# Detailed Design

按模块编写详细设计。coding agent 在 exec 阶段直接读取此文件指导实现。

## 数据来源

**必须读取以下文件：**
- `{task_dir}/.work/architecture.md` — 模块划分、领域模型
- `{task_dir}/.work/requirements.md` — 行为清单
- 项目 CLAUDE.md — 数据库类型、API 风格

## 产出

`{task_dir}/.work/design.md`，按模块组织：

### 每个模块包含

#### 1. 数据库设计

```markdown
## {模块名} — 数据库设计

### 表: users
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 用户唯一标识 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 哈希 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

### 索引
- idx_users_email ON users(email)
```

#### 2. API 设计

```markdown
## {模块名} — API 设计

### POST /api/v1/users/register
注册新用户

Request:
```json
{"email": "user@example.com", "password": "securePass123"}
```

Response 201:
```json
{"id": "uuid", "email": "user@example.com", "created_at": "2025-01-01T00:00:00Z"}
```

Response 409:
```json
{"error": "Email already exists"}
```

Response 422:
```json
{"error": "Validation failed", "details": [{"field": "password", "message": "至少8位"}]}
```
```

#### 3. 模块交互

```markdown
## {模块名} — 模块交互

### 依赖
- user-service: 验证用户身份（HTTP GET /api/v1/users/{id}）

### 被依赖
- notification-service: 订单状态变更时发送通知（事件: order.status_changed）

### 事件发布
- order.created: 订单创建后发布，payload: {order_id, user_id, total_amount}
```

## 约束

- 每个模块独立成节——coding agent 按模块阅读
- API 设计必须包含所有状态码和响应格式
- 模块交互必须明确协议（HTTP/gRPC/消息队列）和方向
- 不写实现代码，不写伪代码——只写接口契约
