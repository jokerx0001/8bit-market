# Frontend E2E Test Patterns

## Playwright 配置

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'only-on-failure',
  },
});
```

## 环境连接模式（本地 E2E）

前端本地 dev server 运行，通过 dev server 代理连开发环境后端（禁止为测试在开发环境后端开 CORS）。

```
本地（E2E 时）              开发环境
┌─────────────────┐        ┌──────────────┐
│ Playwright 浏览器 │        │              │
│   ↓              │        │              │
│ 前端 dev server   │        │  后端服务      │
│ (localhost:{port})│        │              │
│  页面 + /api/*    │ ──代理──→│  API 入口     │
└─────────────────┘        └──────────────┘
```

### 代理配置示例

Vite:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://dev.example.com', // 开发环境 API 入口，从 ops-local.md 环境地址清单读取
        changeOrigin: true,
      },
    },
  },
});
```

webpack:

```javascript
// webpack.dev.js
devServer: {
  proxy: {
    '/api': {
      target: 'https://dev.example.com', // 从 ops-local.md 环境地址清单读取
      changeOrigin: true,
    },
  },
}
```

### 验证方法

dev server 启动后，请求 `http://localhost:{port}/api/<任意接口>`——响应正常（非 CORS 错误）= 代理转发 OK。

### CORS 禁令

- 禁止为测试在开发环境后端开 CORS——白名单扩大攻击面，且掩盖代理配置缺失
- 浏览器报 CORS 错误 = dev server 代理缺失/配置错误 → 修复前端代理配置，不是去后端开 CORS

## 测试结构

```
e2e/
├── auth.setup.ts        # 登录状态保存
├── register.spec.ts     # 注册页面
├── login.spec.ts        # 登录页面
└── products.spec.ts     # 商品页面
```

## 测试模板

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Registration', () => {
  test('successful registration', async ({ page }) => {
    await page.goto('/register');
    // 使用 data-testid 定位（稳定，不依赖 CSS 类名）
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', 'securePass123');
    await page.fill('[data-testid="confirm-password-input"]', 'securePass123');
    await page.click('[data-testid="register-button"]');
    // 验证成功跳转
    await expect(page).toHaveURL('/login');
    await expect(page.locator('[data-testid="success-message"]'))
      .toContainText('注册成功');
  });

  test('email already exists', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[data-testid="email-input"]', 'existing@example.com');
    await page.fill('[data-testid="password-input"]', 'securePass123');
    await page.fill('[data-testid="confirm-password-input"]', 'securePass123');
    await page.click('[data-testid="register-button"]');
    // 验证错误提示
    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('邮箱已被注册');
  });

  test('password too short', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.fill('[data-testid="password-input"]', '123');
    await page.fill('[data-testid="confirm-password-input"]', '123');
    await page.click('[data-testid="register-button"]');
    await expect(page.locator('[data-testid="validation-error"]'))
      .toContainText('至少8位');
  });
});
```

## 页面覆盖清单

每个页面必须覆盖：

- [ ] 正常加载（元素渲染、数据展示）
- [ ] 表单输入与提交（成功路径）
- [ ] 表单验证（失败路径——必填、格式、规则）
- [ ] 导航流转（页面间跳转）
- [ ] 网络错误处理（API 返回错误时的 UI 反馈）
- [ ] 登录态处理（未登录重定向）
