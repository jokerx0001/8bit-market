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

