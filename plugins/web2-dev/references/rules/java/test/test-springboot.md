# Spring Boot 测试指南

## 测试模板

### 单元测试（Service / Util）
#### Service
```java
@SpringBootTest
@ActiveProfiles("local")
class {TargetClass}Test {
    @Resource
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

    // 若有数据回滚要求则这样写
    @Test
    @Transactional
    @Rollback
    public void testSave() {
        // TODO 这个方法里的数据库操作就会最后回滚
    }
}
```

#### Util
```java
class {TargetClass}Test {
    @Test
    void generateSecret() {
        try {
            KeyGenerator keyGen = KeyGenerator.getInstance("HmacSHA256");
            SecureRandom secureRandom = new SecureRandom();
            keyGen.init(256, secureRandom);
            SecretKey secretKey =  keyGen.generateKey();
            System.out.println("秘钥：" + Base64.getEncoder().encodeToString(secretKey.getEncoded()));
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
    }
}
```

## 关键约束

1. **只对 Service 和 Util 编写单元测试**
2. **不写 DTO/Record/VO/Config/Mapper/Entity 的测试**
3. **使用 `@ActiveProfiles("local")` 确保加载 local profile**
4. **测试名称必须清晰描述行为，不使用 "test1" 之类**
5. **一个测试方法只验证一个行为**
6. 使用junit5 jupiter测试.除非根据版本检测到更合适的,这时候直接上报让用户决策
7. 所有的数据库存储逻辑测试都必须有存入成功的case,并且要用用查询语句查询到刚才存储数据,逐字段比对无误才算通过。包括数据库,milvu
s,Elasticsearch
8. UserJwt这种入参对象允许自己创建 例 UserJwt userjwt = new UserJwt(....) 如此来测试
9.如待尝试的Service类的逻辑涉及到properties,yaml等spring配置文件改动，属性配置应写在对应的配置文件里而不是注解里

