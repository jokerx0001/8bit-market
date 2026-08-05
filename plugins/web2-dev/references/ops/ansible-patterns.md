# Ansible Best Practices

## 目录结构

```
ansible/
├── ansible.cfg
├── inventory/
│   ├── dev/
│   │   ├── hosts.yml
│   │   └── group_vars/
│   └── prod/
├── playbooks/
│   ├── postgresql.yml
│   ├── redis.yml
│   └── app.yml
└── roles/
    ├── postgresql/
    ├── redis/
    └── common/
```

## Playbook 模板

### 基础服务部署

```yaml
---
- name: Deploy PostgreSQL
  hosts: database
  become: yes
  vars:
    pg_version: "16"
  tasks:
    - name: Install PostgreSQL
      apt:
        name: "postgresql-{{ pg_version }}"
        state: present
    - name: Start and enable
      systemd:
        name: postgresql
        state: started
        enabled: yes
```

### Role 化（推荐）

复用的组件封装为 role：

```yaml
# roles/postgresql/tasks/main.yml
- name: Install PostgreSQL
  apt:
    name: "postgresql-{{ pg_version }}"
    state: present
```

## 规则

- **幂等性**：所有 playbook 必须可重复执行
- **变量分离**：敏感信息用 ansible-vault
- **标签**：使用 tags 支持部分执行
- **测试**：部署后必须包含验证步骤

## 新增组件流程

1. 检查是否已有对应 role/playbook
2. 无 → 创建 playbook 或 role
3. 测试 playbook（在非生产环境）
4. 执行部署
5. 验证可用性
