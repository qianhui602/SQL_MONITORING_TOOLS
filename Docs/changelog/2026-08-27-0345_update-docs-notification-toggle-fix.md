# 变更记录 - 更新项目文档（通知开关即时生效修复同步）

- **日期**: 2026-08-27 03:45
- **类型**: 配置变更 / 文档更新
- **影响范围**: changelog.md, changelog.en.md, Docs/TECHNICAL_DOCUMENTATION.md, Docs/en/TECHNICAL_DOCUMENTATION.md, Docs/USER_MANUAL.md, Docs/en/USER_MANUAL.md

## 变更内容
将"通知开关配置即时生效"修复（移除 EmailNotifier / FeishuAppNotifier 的 _db_loaded 配置缓存）同步到项目文档，消除文档与代码行为的不一致：

1. **changelog.md / changelog.en.md**
   - 2026-08-26 条目标题追加"通知开关即时生效"，文件清单补充 `backend/app/routers/smtp_test.py`
   - 明细新增 Bug修复条目：移除 _db_loaded 缓存、每次发送前重读数据库配置、关闭开关立即停止发送无需重启；smtp_enabled 关闭时清空 SMTP 字段确保 _is_configured() 返回 False
2. **Docs/TECHNICAL_DOCUMENTATION.md**
   - 版本历史补充 v1.6.0 (2026-08-26) 段落（含飞书应用通知特性与本次 Bug修复），对齐英文版结构
3. **Docs/en/TECHNICAL_DOCUMENTATION.md**
   - v1.6.0 段落追加 toggle 即时生效的 Bug fix 条目
4. **Docs/USER_MANUAL.md / Docs/en/USER_MANUAL.md（16.4 通知配置）**
   - 新增说明：配置保存后立即生效（无需重启服务），关闭邮件/飞书应用通知开关后即刻停止发送

## 变更原因
上一轮修复（_db_loaded 配置缓存导致前端关闭飞书/邮件通知后仍继续发送）只创建了 Docs/changelog 归档，未同步到根 changelog 与 Docs 主文档；且仓库历史在合并整理时中文技术文档丢失了 v1.6.0 版本历史段落。需补齐使全部文档一致。

## 涉及文件
| 文件路径 | 操作 | 说明 |
|---------|---------------------|------|
| changelog.md | 修改 | 补充开关修复条目与文件清单 |
| changelog.en.md | 修改 | 同步英文 |
| Docs/TECHNICAL_DOCUMENTATION.md | 修改 | 补充 v1.6.0 版本历史段落 |
| Docs/en/TECHNICAL_DOCUMENTATION.md | 修改 | v1.6.0 追加修复条目 |
| Docs/USER_MANUAL.md | 修改 | 16.4 新增即时生效说明 |
| Docs/en/USER_MANUAL.md | 修改 | 同步英文 |
