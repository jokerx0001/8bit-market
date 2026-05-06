# Spring Boot Web 测试指南

本文档仅在检测到目标项目是 **Spring Boot Web 项目** 时参考。

## Spring Boot Web 项目识别

满足以下条件视为 Spring Boot Web 项目：
- 存在 `pom.xml` (Maven) 或 `build.gradle` (Gradle)
- 存在 `src/main/java` 目录结构
- `pom.xml` 包含 `spring-boot-starter-web` 依赖

## test profile 配置

### 第一步：检查 application-test 是否存在

按以下优先级检查：
1. `src/test/resources/application-test.yaml`
2. `src/test/resources/application-test.yml`
3. `src/test/resources/application-test.properties`

### 第二步：如果不存在，创建 application-test

**从哪里读取配置：**
1. 项目根目录的 `.env` 文件（如果存在）
2. 项目现有的 `application-*.yaml/yml/properties` 文件（参考风格）

**从 .env 提取的配置项（如果存在）：**
- `DATABASE_URL` / `DB_HOST` / `DB_PORT` / `DB_NAME` → 数据库连接
- `DB_USERNAME` / `DB_PASSWORD` → 数据库凭证
- `REDIS_URL` / `REDIS_HOST` / `REDIS_PORT` → Redis 连接
- `SERVER_PORT` → 服务端口
- 其他自定义配置

**配置风格必须与项目一致：**
- 项目用 `application.yml` → 创建 `application-test.yml`
- 项目用 `application.yaml` → 创建 `application-test.yaml`
- 项目用 `application.properties` → 创建 `application-test.properties`
- 配置项格式、缩进与现有文件保持一致

### 第三步：创建示例

假设检测到：
- `.env` 存在：`DB_HOST=localhost, DB_PORT=5432, REDIS_HOST=localhost`
- 现有风格：`application.yml` (YAML格式，带 `spring:` 前缀)

创建 `src/test/resources/application-test.yml`：
```yaml
spring:
  profiles:
    active: test
  datasource:
    url: jdbc:postgresql://localhost:5432/testdb
    username: testuser
    password: testpass
redis:
  host: localhost
  port: 6379
```

## 测试模板

### 单元测试（Service / Util）

```java
@SpringBootTest(properties = {
    "spring.profiles.active=test"
})
@ActiveProfiles("test")
class {TargetClass}Test {
    @Autowired
    private {TargetClass} target;

    @Test
    void createOrder_withInsufficientStock_throwsException() {
        // Given
        Long productId = 1L;
        int requestedQuantity = 100;
        int availableStock = 10;

        // When & Then
        assertThrows(BusinessException.class, () -> {
            target.createOrder(productId, requestedQuantity);
        });
    }
}
```

### 集成测试（Controller）

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class {TargetController}Test {
    @Autowired private MockMvc mockMvc;

    @Test
    void createOrder_withInvalidRequest_returns400() throws Exception {
        mockMvc.perform(post("/api/orders")
                .contentType("application/json")
                .content("{\"productId\":1,\"quantity\":0}"))
            .andExpect(status().isBadRequest());
    }
}
```

## 关键约束

1. **只对 Service 和 Util 编写单元测试**
2. **不写 DTO/Record/VO/Config/Mapper/Entity 的测试**
3. **使用 `@ActiveProfiles("test")` 确保加载 test profile**
4. **测试名称必须清晰描述行为，不使用 "test1" 之类**
5. **一个测试方法只验证一个行为**
