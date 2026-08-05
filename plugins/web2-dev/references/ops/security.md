# Ops Security — 权限最小化规范

## 核心原则

**所有 AI 可执行的操作必须使用受限账户。超管操作只输出命令，由人工执行。**

## 账户分级

| 级别 | 权限范围 | AI 可执行？ |
|------|---------|------------|
| app-user | 应用代码部署、服务启停 | ✅ 是 |
| db-user | 指定数据库的 CRUD + DDL | ✅ 是 |
| db-admin | 所有数据库管理 | ❌ 只输出命令 |
| sudo-user | 系统级操作（安装软件、配置服务） | ❌ 只输出命令 |
| root | 无限制 | ❌ 绝不使用 |

## CLAUDE.md 中的账户声明

```markdown
## 服务器账户

### 开发服务器 (dev.example.com)
- SSH: app-deploy@dev.example.com
- 权限: /opt/app/ 读写, systemctl restart myapp
- sudo: 仅 systemctl restart myapp

### 数据库 (dev.example.com:5432)
- 账户: app_user / ***（从 ansible-vault 获取）
- 权限: myapp_db 的 CRUD + DDL

### Ansible 项目
- 路径: /home/devops/ansible/
- 执行账户: ansible-runner
```

## 禁止事项

- ❌ 使用 root 账户执行任何操作
- ❌ 使用数据库 superuser 账户
- ❌ AI 自行执行 sudo 命令
- ❌ 在代码或配置中硬编码凭据
- ❌ 将超管密码传入 AI prompt

## 超管操作流程

1. AI 分析需求，输出需要执行的完整命令
2. 人工审核命令
3. 人工执行
4. 人工确认结果
5. AI 继续后续步骤

## 超管操作示例

当需要安装 PostgreSQL 时：
```bash
# AI 输出以下命令供人工执行：
ansible-playbook -i inventory/dev playbooks/postgresql.yml --become

# 人工审核、执行、确认后，AI 继续：
# "已确认 PostgreSQL 安装完成，正在创建应用数据库..."
```
