# Change Log - Fixed Missing Comma After faq Property in Help.vue

[简体中文](../../changelog/2026-07-30-0905_Help_vue_faq_comma_fix.md) | **English**

- **Date**: 2026-07-30 09:05
- **Type**: Bug fix
- **Scope**: Frontend help page / Docker frontend build

## Changes
In the `sectionContents` object of `frontend/src/views/Help.vue`, a missing comma was added after the `faq` property's template string (line 484, changing `` ` `` to `` `, ``) so the following `contact` property can be parsed correctly.

Before:
```javascript
      <p>A：理论上没有上限，但建议单实例部署监控不超过 50 个 SQL Server 实例。超过 50 个建议关注后端服务器的资源占用情况，必要时进行水平扩展。</p>
    `
  contact: `
```

After:
```javascript
      <p>A：理论上没有上限，但建议单实例部署监控不超过 50 个 SQL Server 实例。超过 50 个建议关注后端服务器的资源占用情况，必要时进行水平扩展。</p>
    `,
  contact: `
```

## Reason
When building the frontend image with Docker, Vite/Vue compilation of `Help.vue` failed with:
```
Unexpected token, expected ","
```
The error pointed to the line of the `contact` property in the `sectionContents` object. The root cause was a missing comma at the end of the `faq` property's template string from a previous fix, making the object literal syntax invalid and breaking the entire frontend build.

## Files Involved
| File | Action (add/modify/delete) | Description |
|------|---------------------------|-------------|
| frontend/src/views/Help.vue | Modified | Added the comma after the faq property, fixing the object literal syntax |

## Verification
- Verified with Grep: the `sectionContents` object has 16 properties (overview / dashboard / performance / deadlocks / alerts / 'slow-queries' / blocking / disk / indexes / 'alert-rules' / instances / report / settings / users / faq / contact), each ending with a comma, with the final `contact` correctly closed by `}`.
- Committed and pushed to GitHub `origin/master`: commit `02d01c5`, push result `f22fbd6..02d01c5 master -> master`.
- Docker Desktop was not available on this machine, so `docker compose up -d --build` was not run locally; please run it on a machine with Docker to complete final verification.
