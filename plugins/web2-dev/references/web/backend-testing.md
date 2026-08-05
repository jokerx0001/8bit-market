# Backend Integration Test Patterns

## 测试结构

```
integration/
├── conftest.py          # fixtures: 服务启动、DB 重置、认证 token
├── test_users.py        # 用户模块测试
├── test_products.py     # 商品模块测试
└── test_orders.py       # 订单模块测试
```

## 每种语言模板

### Python (pytest + requests)

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

def test_register_success():
    resp = requests.post(f"{BASE_URL}/users/register", json={
        "email": "test@example.com",
        "password": "securePass123"
    })
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["email"] == "test@example.com"

def test_register_duplicate_email():
    # 先注册一次
    requests.post(f"{BASE_URL}/users/register", json={
        "email": "dup@example.com", "password": "securePass123"
    })
    # 再注册相同邮箱
    resp = requests.post(f"{BASE_URL}/users/register", json={
        "email": "dup@example.com", "password": "anotherPass456"
    })
    assert resp.status_code == 409
    assert "already exists" in resp.json()["error"].lower()
```

### Go (testing + net/http)

```go
func TestRegisterSuccess(t *testing.T) {
    body := `{"email":"test@example.com","password":"securePass123"}`
    resp, _ := http.Post(baseURL+"/users/register", "application/json",
        strings.NewReader(body))
    assert.Equal(t, 201, resp.StatusCode)
}
```

### Java (SpringBootTest + TestRestTemplate)

```java
@Test
void registerSuccess() {
    var request = Map.of("email", "test@example.com", "password", "securePass123");
    var resp = restTemplate.postForEntity("/api/v1/users/register", request, Map.class);
    assertEquals(HttpStatus.CREATED, resp.getStatusCode());
}
```

## 测试场景覆盖清单

每个模块的每个 API 接口必须覆盖：

- [ ] 成功场景（正常输入 → 预期成功响应）
- [ ] 参数缺失（必填字段为空 → 422/400）
- [ ] 参数格式错误（非法邮箱、过短密码 → 422/400）
- [ ] 业务规则违反（重复、冲突、限制 → 409/403）
- [ ] 认证缺失（无 token → 401）
- [ ] 权限不足（非管理员操作管理接口 → 403）
