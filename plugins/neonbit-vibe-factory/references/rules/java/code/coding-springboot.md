# Spring Boot

## properties
- 支持外部更改的属性,使用Properties类来管理,使用配置中心,且支持动态刷新
```java
@ConfigurationProperties(prefix = "app.example")
@Configuration
@Data
public class ExampleProp {
    /**
     * 过期时长(s)
     */
    private Long expiration = 604800L;

    /**
     * 开关
     */
    private Boolean enabled = false;
}
- 区分其他组件的配置和自己写的配置。properties或者yaml配置文件中,自己的配置统一 app.应用英文名 开头
```properties
app.user.log.dir=/var/log/app/users
```
```yaml
app:
  user:
    log:
      dir: /var/log/app/users
```

## controller层
- 只处理HTTP请求和响应，调用service层执行业务逻辑。
- 不允许在controller里写业务逻辑
- 不允许在controller里访问数据库
- Use Bean Validation (@NotNull, @NotBlank, @Size) on DTOs
```java
    public ApiResponse<String> update(@RequestBody @Valid UpdateUserVO updateUserVO) {
        userService.update(updateUserVO);
        return ApiResponse.ok("User updated");
    }

public record UpdateUserVO(@NotNull(message = "用户Id不能为空") Long id, String phone, String name, Integer gender, String email) {}
```
- 各业务在自己的类里集中管理，譬如App相关的接口都放在AppController里，User相关的接口都放在UserController里。

## service层
- 处理核心业务逻辑，调用repository层访问数据库
- 业务分类要遵守,譬如AppService只处理App相关的业务，UserService只处理User相关的业务。

## 工具类
### 如时间处理,加解密等不需要维护状态的工具类，应该设计为无状态的静态工具类。
- 只包含静态方法，不依赖于实例状态
- 命名以Utils结尾，如DateUtils、StringUtils
- 只包含与工具相关的方法，不包含业务逻辑
- 不要重复造轮子，优先使用已存在或Java标准库或第三方库提供的工具类。只有当现有工具类无法满足需求时，才创建新的工具类。
- 不确定的内容应该由调用者传入参数，而不是在工具类内部硬编码。
```java
public class DateUtils {
    public static String formatDate(LocalDate date) {
        return date.format(DateTimeFormatter.ISO_DATE);
    }
}
```

### 外部组件封装工具类
- 封装对外部组件（如Redis、Kafka）的访问逻辑，提供简化、通用的接口
- 命名以ComponentUtils结尾，如RedisUtils、KafkaUtils
- 只包含与组件访问相关的方法，不包含业务逻辑。禁止任何与业务相关的成员和方法。
- 使用properties风格搭配@Configuration和@Bean来注入核心bean
```java
/**
 * milvus客户端配置属性类
 */
@ConfigurationProperties(prefix = "milvus")
@Component
@RefreshScope
@Getter
@Setter
public class MilvusClientProp {

    /**
     * 服务地址
     */
    private String host = "localhost";

    /**
     * 端口
     */
    private Integer port = 19530;

    private String uri;
}

@Configuration
public class MilvusClientConfiguration {

    @Resource
    private MilvusClientProp milvusClientProp;

    /**
     * 构建milvusclientv2 bean
     * @return
     */
    @Bean
    public MilvusClientV2 milvusClientV2() {
        String uri = milvusClientProp.getUri();
        if (StringUtils.isEmpty(uri)) {
            uri = String.format("http://%s:%s", milvusClientProp.getHost(), milvusClientProp.getPort());
        }
        ConnectConfig connectConfig = ConnectConfig.builder()
                .uri(uri)
                .dbName(milvusClientProp.getDatabaseName())
                .build();
        // ...仅做示范 还有很多其他配置
        return new MilvusClientV2(connectConfig);
    }
}
```
