---
name: web2-dev:service-ops
description: |
  服务运维 skill。负责应用部署、启停、回滚。
  部署方式严格遵循 ops-local.md，不自行决定。

  <example>
  assistant: "使用 service-ops skill 将用户模块部署到开发服务器。"
  </example>
---

# Service Ops — 服务运维

部署应用代码到服务器，管理启停。

**必须读取：**
- 项目根目录 `ops-local.md` — 部署方式、服务器地址、账户、启停命令
- `${CLAUDE_PLUGIN_ROOT}/references/ops/security.md` — 安全规范

## 执行规则

### 1. 严格遵循 ops-local.md

不自行决定部署方式。ops-local.md 中怎么写就怎么执行。

### 2. 部署后健康检查

每次部署后执行健康检查，确认服务正常运行。

### 3. 提供回滚方式

部署前记录当前版本/commit，如健康检查失败，提供回滚命令。

### 4. 权限最小化

仅作本次部署相关操作。不做无关修改。

## 部署流程

```
1. 读 ops-local.md → 获取部署方式
2. 部署前 → 记录当前状态（commit hash、运行状态）
3. 执行部署命令
4. 健康检查 → curl /health 或对应检查端点
5. 失败 → 输出部署失败报告
6. 成功 → 输出部署报告
```

## 部署报告格式

```
## 部署报告

**服务**: {服务名}
**目标**: {服务器}
**版本**: {commit hash}
**部署时间**: {timestamp}
**健康检查**: ✅ 通过
**回滚命令**: ssh {user}@{host} "cd {path} && git checkout {prev_commit} && systemctl restart {service}"
```
