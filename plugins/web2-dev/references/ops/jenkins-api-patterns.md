# Jenkins API 操作模式

所有 Jenkins 操作走 **REST API + API token**。不要模拟浏览器表单登录（crumb 流程）。

## 环境变量（本插件约定）

| 变量 | 用途 |
|------|------|
| `JENKINS_USER` | Jenkins 用户名 |
| `JENKINS_API_TOKEN` | Jenkins API token |

值由项目根 `.env` 提供（Claude Code 自动加载）。命令只用变量引用形式（`"$JENKINS_USER:$JENKINS_API_TOKEN"`），禁止 Read/cat/grep `.env`、禁止 echo/printenv 变量值。

## 认证

官方原文（Authenticating scripted clients）：

> "use HTTP BASIC authentication to specify the user name and the API token"

```bash
curl --user "$JENKINS_USER:$JENKINS_API_TOKEN" <jenkins-url>/...
```

- **token 生成位置（官方）：** 右上角用户名 → Security 查看 API token；快捷方式 `$root/me/security`
- **官方警告：** Jenkins 不发认证质询（返回 403 而非 401），凭据必须在首次请求就带上
- **CSRF（官方）：** "API tokens are preferred instead of crumbs for CSRF protection" —— API token 认证不需要 crumb；用密码时才需要 crumb（crumb 与 session 绑定，提取 crumb 后丢失 cookie 必然失败）

## 操作

### 查看构建状态

Remote Access API 的 JSON 端点（`.../api/` 提供 XML / JSON / JSONP / Python JSON 输出）：

```bash
curl -u "$JENKINS_USER:$JENKINS_API_TOKEN" \
  "https://{jenkins}/job/{jobName}/lastBuild/api/json" | jq -r '.result'
```

返回 `SUCCESS` / `FAILURE` / `UNSTABLE` / `ABORTED`。

官方原文：对某次构建的 URL 追加 `/api/` 即得该构建的 API 输出；"See `.../api/` on your Jenkins server for more up-to-date details."

### 触发构建

官方原文（Remote Access API）：

> "You merely need to perform an HTTP POST on `JENKINS_URL/job/JOBNAME/build`"

```bash
curl -X POST -u "$JENKINS_USER:$JENKINS_API_TOKEN" \
  "https://{jenkins}/job/{jobName}/build"
```

- 参数化 job 用 `buildWithParameters`（官方示例：`--data id=123`、`--form FILE=@PATH`，@ 后必须是绝对路径）
- 对多分支流水线 / Organization Folder 执行此 POST = 触发一次扫描（官方原文："This also works for Multibranch Pipelines and Organization Folders. It would trigger a scan."）

### 验证 Jenkinsfile（提交前，Declarative Pipeline linter）

官方原文（Pipeline Development Tools）：

```bash
curl -X POST --user "$JENKINS_AUTH" -F "jenkinsfile=<Jenkinsfile" \
  "$JENKINS_URL/pipeline-model-converter/validate"
```

其中 `$JENKINS_AUTH = your_username:api_token`（即 `"$JENKINS_USER:$JENKINS_API_TOKEN"`）。

- 合法输出（官方）：`Jenkinsfile successfully validated.`
- 非法输出（官方）：`Errors encountered validating Jenkinsfile: ...`
- 官方推荐的替代方式（SSH）：`ssh -p $JENKINS_PORT $JENKINS_HOST declarative-linter < Jenkinsfile`

## 不要做

- 模拟浏览器表单登录（`j_spring_security_check` + crumb 提取）：crumb 与 session 绑定，官方明确推荐用 API tokens 代替 crumbs
- 用密码认证：官方原文 "using your real password is still supported, but it is not recommended"

## 本指南中没有的内容查阅官方文档了解

## 来源（官方文档）

- Remote Access API: https://www.jenkins.io/doc/book/using/remote-access-api/
- Authenticating scripted clients: https://www.jenkins.io/doc/book/system-administration/authenticating-scripted-clients/
- Pipeline Development Tools（linter）: https://www.jenkins.io/doc/book/pipeline/development/
