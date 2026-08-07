# Spring Boot 微服务部署模式

已验证的 Spring Boot Web 后端标准部署方案。service-ops 遇到 Spring Boot 项目时按此模式执行。

## 部署结构

```
{项目根目录}/
├── Dockerfile                        # 镜像定义
├── deploy/
│   ├── build_docker_image.sh         # 构建 + 推送
│   ├── start.sh                      # 启动容器
│   └── stop.sh                       # 停止容器
├── Jenkinsfile                       # CI/CD 编排（可选）
└── deploy/nginx-{app}.conf           # Nginx 反代（有前端时）

目标服务器:
/data/deploy/{container_name}/        # deploy 脚本存放
/data/deploy/logs/                    # 日志挂载
/data/deploy/www/{app}/               # 前端静态文件（有前端时）
```

## 部署流程

```
1. Maven 构建
   mvn -f {project}/pom.xml clean package -DskipTests

2. Docker 镜像构建 + 推送
   export REGISTRY_URL=... REGISTRY_IMAGE_NAME=... BUILD_CONTEXT=...
   sh deploy/build_docker_image.sh

3. 部署到目标服务器
   scp deploy/start.sh deploy/stop.sh → /data/deploy/{container_name}/
   ssh → docker login → stop.sh → start.sh

4. 前端（如有）
   pnpm build → scp dist/ → /data/deploy/www/{app}/
   Nginx 配置部署到 /etc/nginx/sites-enabled/
```

## 约定

| 项目 | 约定 |
|------|------|
| 容器名 | 等于项目名（如 `chance-view`） |
| 网络 | `--network=host`，容器直接使用宿主机网络 |
| 重启策略 | `--restart always` |
| 卷挂载 | `/data/deploy/logs` + `/data/deploy/{container_name}` |
| 配置中心 | Nacos，环境变量注入（前缀 + `_NACOS_ADDR/NAMESPACE/USERNAME/PASSWORD`） |
| Spring profile | `cntr`（容器环境），Dockerfile CMD 中指定 |
| 前端工具 | pnpm（Node.js 项目） |
| 前端路径 | `/data/deploy/www/{app}/` |
| Nginx | SSL + SPA（try_files）+ `/api/` 反代 localhost:8080 |
| 部署账户 | 受限账户，属组 `developer` |
| 连接方式 | SSH config 别名，不在配置文件中写 IP |

## 模板适配指南

模板存放在 `${CLAUDE_PLUGIN_ROOT}/references/ops/templates/springboot/`。
使用时读取模板，将占位符替换为项目实际值。

### 变量映射表

从 `ops-local.md` 和项目特征中提取变量值：

| 占位符 | 来源 | 示例 |
|--------|------|------|
| `{{PROJECT_NAME}}` | pom.xml artifactId（后端）或项目目录名 | chance-view |
| `{{JAVA_VERSION}}` | pom.xml java.version | 17 |
| `{{SPRING_PROFILE}}` | 约定 cntr，或 ops-local.md 指定 | cntr |
| `{{CONTAINER_NAME}}` | 项目名 | chance-view |
| `{{ENV_PREFIX}}` | 组织名大写（从 package/groupId 提取） | NEONBIT |
| `{{DEPLOY_SERVER}}` | ops-local.md | (SSH 别名或 IP) |
| `{{DEPLOY_USER}}` | ops-local.md | opsbot |
| `{{REGISTRY_URL}}` | ops-local.md | registry.example.com |
| `{{JDK_TOOL}}` | pom.xml java.version 映射 | openjdk17 |
| `{{MAVEN_TOOL}}` | pom.xml 或项目约定 | apache-maven-3.9.5 |
| `{{NODEJS_TOOL}}` | 前端 package.json 或项目约定 | nodejs26 |
| `{{FRONTEND_APP}}` | 前端目录名 | buffett-ui |
| `{{FRONTEND_INSTALL_CMD}}` | pnpm install / npm install | pnpm install |
| `{{FRONTEND_BUILD_CMD}}` | pnpm run build / npm run build | pnpm run build |
| `{{FRONTEND_DEPLOY_PATH}}` | 约定 /data/deploy/www/{app}/ | /data/deploy/www/buffett/ |
| `{{SERVER_NAME}}` | ops-local.md | buffett.neonbit.top |
| `{{UPSTREAM_NAME}}` | 项目名下划线命名 | chance_view |
| `{{SSL_CERT_PATH}}` | ops-local.md | /data/ssl/neonbit.top.cer |
| `{{SSL_KEY_PATH}}` | ops-local.md | /data/ssl/neonbit.top.key |

### 适配步骤

1. 读取 pom.xml，提取 `artifactId`、`java.version`、`groupId`
2. 读取 ops-local.md，获取服务器、Registry、证书路径
3. 检测是否存在前端目录（`package.json`、`vite.config.*` 等）
4. 读取模板文件，逐个替换占位符
5. 将替换后的文件写入项目对应路径

### 模板选择

| 条件 | 使用的模板 |
|------|-----------|
| 必有 | Dockerfile, build_docker_image.sh, start.sh, stop.sh |
| 有 CI/CD 需求 | Jenkinsfile |
| 有前端 | nginx.conf，Jenkinsfile 中开启 `HAS_FRONTEND` 块 |

### 不适用的情况

此模式依赖于：
- Docker + 私有 Registry
- Nacos 配置中心
- `--network=host` 网络模式
- `/data/deploy/` 目录约定
- Jenkins CI/CD

如果 ops-local.md 中声明了不同的部署方式，以 ops-local.md 为准，此模式仅作参考。
