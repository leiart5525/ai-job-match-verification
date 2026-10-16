# AI Job Match & Verification

中文求职 Agent Skill：岗位发现、来源核验、经历匹配与投递跟踪。

**没写的技能不等于不会；未核验不等于正在招聘；404不代表岗位关闭。**

## 安装：复制给你的 Agent

> 请从 https://github.com/leiart5525/ai-job-match-verification 安装 ai-job-match-verification Skill。先检查仓库内容，找到包含 SKILL.md 的 skills/ai-job-match-verification 文件夹，完整安装到当前工具支持的技能目录，不要覆盖已有同名安装。检查搜索、简历解析和 Excel 导出环境，告诉我哪些能力已验证可用，以及是否需要重新加载。

当前代码位于仓库的 ai-job-match-verification 文件夹内，Agent 应保留 Skill 内部的 scripts 和 references 目录。

## 开始使用

> 我之前做策略增长运营，主要考虑上海，帮我找一下最近在招的岗位。

Skill 会复用已提供的信息，补问缺少的岗位方向、地点、工作年限和最高学历；同时邀请你补充薪资、行业、技能、项目或简历。可选信息不阻塞搜索。

- 没有足够经历证据：先按岗位职责判断方向相关性，不虚构个人匹配。
- 有具体经历：逐项对照JD，解释有证据支持的能力与待确认项，不生成匹配百分比。
- 官网与第三方双渠道发现岗位，保留真实链接、核验时间与访问限制。
- 默认展示最多10条推荐，完整 Excel 包含全部岗位、推荐、投递跟踪和核验日志。
- 可以说“J002不考虑了”“J001已投递”“重新核验历史岗位”，稳定编号与投递状态会保留。

## 中文演示与文档

- [中文对话演示](ai-job-match-verification/docs/中文演示.md)
- [安装说明](ai-job-match-verification/docs/安装说明.md)
- [详细说明与开发者安装](ai-job-match-verification/README.md)
- [测试报告](ai-job-match-verification/TEST-REPORT.md)

## 环境与边界

需要支持 Agent Skills、文件操作与脚本执行的 Agent；基础脚本需要 Python 3.10+，岗位搜索需要宿主联网搜索／浏览能力。PDF、Word 与 Excel 导入依赖按需配置。自带 Excel 导出器需要 Node.js 和可用的 @oai/artifact-tool；已在提供该运行时的环境验证，其他环境须实际检查。未成功导出时不会声称 Excel 已生成。

不自动投递、不发送邮件或微信、不自动修改原简历。私人求职档案保存在用户工作目录。中文演示中的虚构案例已标注；历史真实岗位观察不代表现在仍在招。

MVP v0.1.4 · 35项底层回归测试通过；具体测试范围与限制见测试报告。
