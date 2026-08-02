# 变更记录 - 修复 Help.vue 中 faq 属性后缺少逗号的语法错误

- **日期**: 2026-07-30 09:05
- **类型**: Bug修复
- **影响范围**: 前端帮助页面 / Docker 前端构建

## 变更内容
在 `frontend/src/views/Help.vue` 文件的 `sectionContents` 对象中，`faq` 属性的模板字符串结束后补上了缺失的逗号（第 484 行，将 `` ` `` 改为 `` `, ``），使后续的 `contact` 属性可以被正确解析。

修复前：
```javascript
      <p>A：理论上没有上限，但建议单实例部署监控不超过 50 个 SQL Server 实例。超过 50 个建议关注后端服务器的资源占用情况，必要时进行水平扩展。</p>
    `
  contact: `
```

修复后：
```javascript
      <p>A：理论上没有上限，但建议单实例部署监控不超过 50 个 SQL Server 实例。超过 50 个建议关注后端服务器的资源占用情况，必要时进行水平扩展。</p>
    `,
  contact: `
```

## 变更原因
Docker 构建前端镜像时，Vite/Vue 编译 `Help.vue` 报错：
```
Unexpected token, expected ","
```
错误指向 `sectionContents` 对象中 `contact` 属性所在行。根因是上一轮修复时 `faq` 属性的模板字符串结尾遗漏了逗号，导致对象字面量语法不合法，从而中断整个前端构建流程。

## 涉及文件
| 文件路径 | 操作（新增/修改/删除） | 说明 |
|---------|---------------------|------|
| frontend/src/views/Help.vue | 修改 | 补充 faq 属性后的逗号，修复对象字面量语法 |

## 验证
- 已通过 Grep 核对：`sectionContents` 对象共 16 个属性（overview / dashboard / performance / deadlocks / alerts / 'slow-queries' / blocking / disk / indexes / 'alert-rules' / instances / report / settings / users / faq / contact），每个属性结尾均带逗号，最后 `contact` 由 `}` 正确闭合。
- 已提交并推送到 GitHub `origin/master`：commit `02d01c5`，推送结果 `f22fbd6..02d01c5 master -> master`。
- 由于 Docker Desktop 不在本机，未在本机执行 `docker compose up -d --build` 验证；请在具备 Docker 环境的机器上执行该命令以完成最终验证。
