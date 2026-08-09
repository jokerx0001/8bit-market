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

### 5. Spring Boot 项目部署

检测到项目为 Spring Boot Web 后端时，按已验证的标准模式部署。ops-local.md 无特殊声明则采用此模式。

**结构参考：** 读取 `${CLAUDE_PLUGIN_ROOT}/references/ops/springboot-deploy-pattern.md`，了解完整部署结构、约定和适配步骤。

**模板文件：** `${CLAUDE_PLUGIN_ROOT}/references/ops/templates/springboot/` 下 6 个模板：
`Dockerfile`、`build_docker_image.sh`、`start.sh`、`stop.sh`、`nginx.conf`、`Jenkinsfile`。

**适配流程：**

1. 读取 `pom.xml` → 提取 `artifactId`、`java.version`、`groupId`
2. 读取 `ops-local.md` → 获取服务器、Registry、域名、证书路径
3. 按 springboot-deploy-pattern.md 的变量映射表，逐个替换模板占位符
4. 将替换后的文件写入项目对应路径
5. 按 springboot-deploy-pattern.md 的部署流程执行

**注意：** ops-local.md 中如声明了不同的部署方式（非 Docker、非 Nacos 等），以 ops-local.md 为准，模板仅作参考。

## 部署流程

```
1. 读 ops-local.md → 获取部署方式
2. 部署前 → 记录当前状态（commit hash、运行状态）
3. 执行部署命令
4. 健康检查 → curl /health 或对应检查端点
5. 失败 → 输出部署失败报告
6. 成功 → 输出部署报告
```

## Jenkins 部署与操作

ops-local.md 声明了 Jenkins 部署方式时，按本节执行。

### Jenkins 操作要求

所有 Jenkins 操作使用 Jenkins API（REST API + API token）。具体命令与官方文档见 `${CLAUDE_PLUGIN_ROOT}/references/ops/jenkins-api-patterns.md`。

**禁止模拟浏览器表单登录**（`j_spring_security_check` + crumb 流程）。

### 环境变量（Jenkins API 认证）

值由项目根 `.env` 提供，Claude Code 自动加载：

| 变量 | 用途 |
|------|------|
| `JENKINS_USER` | Jenkins 用户名 |
| `JENKINS_API_TOKEN` | Jenkins API token（Jenkins 用户设置页 Security → API Token 生成，只显示一次） |

- 命令只准用变量引用形式（`"$JENKINS_USER:$JENKINS_API_TOKEN"`），日志不落真实值
- 禁止 Read/cat/grep `.env` 文件，禁止 echo/printenv 变量值
- 变量缺失 → 输出配置说明并停止，**不得降级用密码登录**

### 部署状态检查

- 部署触发后（分支 push 或 API 触发），必须检查部署是否成功
- 构建可能仍在进行中（部署中）→ 查询最新构建状态确认结果
- 构建失败 → 寻找原因并解决问题（查看构建日志/错误输出），不得把失败当完成

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
