---
name: web2-dev:infra-ops
description: |
  基础设施运维 skill。管理 Ansible 项目完成基础环境部署（数据库、中间件、OS 配置）。
  所有部署必须通过 Ansible playbook，不允许裸命令。部署后必须测试可用性。

  <example>
  Context: exec 阶段 1 — 任务循环开始前
  assistant: "使用 infra-ops skill 部署 PostgreSQL 和 Redis。"
  </example>
---

# Infrastructure Ops — 基础设施运维

管理 Ansible 项目，完成基础环境部署。可追溯、可复现。

## 数据来源

**必须读取：**
- 项目 CLAUDE.md — Ansible 项目路径、基础设施服务器地址、账户
- `${CLAUDE_PLUGIN_ROOT}/references/ops/ansible-patterns.md` — Ansible 最佳实践
- `${CLAUDE_PLUGIN_ROOT}/references/ops/security.md` — 安全规范

## 执行规则

### 1. 只用 Ansible

所有环境变更必须通过 Ansible playbook/role：
```
ansible-playbook -i inventory/{env} playbooks/{component}.yml
```

**禁止：**
- ssh 手动执行命令
- apt/yum install 裸命令
- docker run 裸命令
- 手动编辑配置文件

### 2. 缺失的组件 → 新增 playbook

Ansible 项目中无对应 playbook 时：
1. 按 `${CLAUDE_PLUGIN_ROOT}/references/ops/ansible-patterns.md` 创建
2. 测试通过后执行部署
3. 保证后续可复用

### 3. 权限最小化

- 使用 CLAUDE.md 中声明的受限账户
- 超管操作（sudo/root）只输出完整命令，由人工执行
- 数据库操作使用 CLAUDE.md 中声明的受限账户

### 4. 部署完必须测试

每个组件部署完成后验证：
- 端口监听：`ss -tlnp | grep {port}`
- 服务状态：`systemctl status {service}`
- 连接测试：对应客户端的连接命令
- API 响应（如适用）

## 常用组件部署模板

### PostgreSQL
```yaml
# playbooks/postgresql.yml
- hosts: database
  vars:
    pg_version: "16"
    db_name: "{{ app_db }}"
    db_user: "{{ app_user }}"
    db_password: "{{ vault_app_db_password }}"
  roles:
    - postgresql
```

### Redis
```yaml
# playbooks/redis.yml
- hosts: cache
  vars:
    redis_maxmemory: "256mb"
  roles:
    - redis
```

## 测试清单

| 组件 | 测试方式 |
|------|---------|
| PostgreSQL | `psql -h {host} -U {user} -d {db} -c "SELECT 1"` |
| Redis | `redis-cli -h {host} PING` |
| Nginx | `curl -sI {host} | grep "200 OK"` |
| 应用服务 | `curl -s {health_endpoint} | grep "ok"` |
