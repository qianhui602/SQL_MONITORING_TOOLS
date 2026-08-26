# 变更记录 - 更新项目文档（飞书应用通知相关特性）

- **日期**: 2026-08-26 15:27
- **类型**: 配置变更 / 文档更新
- **影响范围**: README.md, README.en.md, changelog.md, changelog.en.md, Docs/ 下中英文项目文档、技术文档、用户手册

## 变更内容
同步补充自 v1.6.0 阶段以来的功能特性说明，使项目文档与代码现状一致：

1. **README.md / README.en.md**
   - "告警与通知"章节从"仅企业微信通知"扩充为完整渠道矩阵：多渠道组合通知、关键错误飞书应用通知（open_id/邮箱接收人，自动识别 receive_id_type）、钉钉/企业微信/飞书群机器人 Webhook、SMTP 邮件、渠道卡片弹窗配置与一键测试
   - "功能说明"新增"通知渠道配置"条目
2. **changelog.md / changelog.en.md**
   - 新增 2026-08-26 条目：关键错误飞书应用通知 / 接收人邮箱支持 / 通知渠道配置弹窗化 / 侧边栏布局修复
3. **Docs/PROJECT_DOCUMENTATION.md（及英文版）**
   - 1.3.6 通知服务补充飞书机器人通知、飞书应用通知、渠道测试三个能力项
   - 环境变量表新增 `FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_RECEIVE_OPEN_ID`
   - 运行时配置说明更新为"Webhook 与飞书应用通知配置"
4. **Docs/TECHNICAL_DOCUMENTATION.md（及英文版）**
   - NotificationService 示例代码补充 FeishuNotifier 与 FeishuAppNotifier 渠道分发逻辑（feishu_app 仅 critical 触发）
   - 故障排查"告警通知没有发送"补充飞书应用排查项（启用机器人能力 + im:message:send_as_bot 权限，errCode 230006）
   - 版本历史新增 v1.6.0 (2026-08-26)
5. **Docs/USER_MANUAL.md（及英文版）**
   - 16.4 通知配置重写为卡片式渠道配置 + 弹窗操作流程，说明接收人格式与权限前置要求

## 变更原因
近期功能迭代（飞书应用通知、邮箱接收人支持、设置页通知渠道改版、侧边栏布局修复）已合入 master，但 README/changelog/Docs 均未反映这些变化；文档与实际能力不一致会误导部署与运维。

## 涉及文件
| 文件路径 | 操作 | 说明 |
|---------|---------------------|------|
| README.md | 修改 | 告警与通知、功能说明章节更新 |
| README.en.md | 修改 | 同步英文 |
| changelog.md | 修改 | 新增 2026-08-26 条目 |
| changelog.en.md | 修改 | 同步英文 |
| Docs/PROJECT_DOCUMENTATION.md | 修改 | 通知服务、环境变量表、运行时配置 |
| Docs/en/PROJECT_DOCUMENTATION.md | 修改 | 同步英文 |
| Docs/TECHNICAL_DOCUMENTATION.md | 修改 | 通知服务示例、FAQ、版本历史 v1.6.0 |
| Docs/en/TECHNICAL_DOCUMENTATION.md | 修改 | 同步英文 |
| Docs/USER_MANUAL.md | 修改 | 16.4 通知配置重写 |
| Docs/en/USER_MANUAL.md | 修改 | 同步英文 |
