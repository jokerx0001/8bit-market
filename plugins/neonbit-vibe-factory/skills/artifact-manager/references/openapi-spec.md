# OpenAPI 3.0 格式规范

接口文档必须遵循 OpenAPI 3.0 规范，使用 YAML 格式。

## 核心结构

```yaml
openapi: 3.0.3
info:
  title: API 名称
  description: API 描述
  version: 1.0.0
servers:
  - url: http://localhost:8080/api
    description: 开发服务器
paths:
  /users:
    get:
      summary: 获取用户列表
      tags:
        - 用户管理
      parameters:
        - name: page
          in: query
          schema:
            type: integer
          description: 页码
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
    post:
      summary: 创建用户
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: 创建成功
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        username:
          type: string
        email:
          type: string
    UserList:
      type: object
      properties:
        total:
          type: integer
        users:
          type: array
          items:
            $ref: '#/components/schemas/User'
    CreateUserRequest:
      type: object
      required:
        - username
        - email
      properties:
        username:
          type: string
        email:
          type: string
        password:
          type: string
```

## 必须包含的字段

- `openapi`: 版本号 (3.0.x)
- `info.title`: API 标题
- `info.version`: 版本
- `paths`: 所有端点路径
- `components/schemas`: 数据模型定义

## 每个接口必须包含

- `summary`: 接口摘要
- `parameters` (如有): 参数定义
- `requestBody` (如有): 请求体 schema
- `responses`: 响应定义，包含 statusCode 和 responseBody