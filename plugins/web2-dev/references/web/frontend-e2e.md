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
