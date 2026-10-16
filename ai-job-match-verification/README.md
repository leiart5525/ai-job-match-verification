# AI Job Match & Verification

一个可复用的 Agent Skill：发现真实职位、保留来源证据、按经历匹配，并维护本地投递记录。MVP 0.1.4。

**Unknown 不等于不会；未核验不等于在招；同名不等于同一职位。**

[中文使用演示](docs/中文演示.md) · [让 Agent 帮你安装](docs/安装说明.md)

## 安装

最简单的方式：把本仓库链接或解压后的项目文件夹交给 Agent，让它安装 `skills/ai-job-match-verification`，检查环境并说明哪些功能可用。可直接复制[安装说明](docs/安装说明.md)中的提示词。以下为手动安装方式。

下载仓库后，在仓库根目录运行：

```sh
python3 install.py --dest "$HOME/.codex/skills"
```

安装器不会覆盖已有同名 Skill。重启或重新加载支持 Agent Skills 的宿主，再输入：

> 使用 $ai-job-match-verification 帮我发现 AI 产品岗位。先用 Discovery Mode；保存到当前项目的 private/，给我 Top 10 和完整 Excel。

其他宿主：将 `skills/ai-job-match-verification` 整个文件夹复制到该宿主的技能目录。本地宿主已实跑自然语言入口、中文简历、真实中文搜索的降级和四表Excel链路；其他宿主发现机制未经验证。

基础运行需 Python 3.10+ 和支持读取 Skill、浏览/搜索、执行脚本与本地文件的 Agent。helper 本身**不联网、不调用模型**；搜索和 JD 语义分析由宿主 Agent 完成。无网络时可以分析用户提供的 JD，但必须展示 Unverified。

可选 Python 依赖：

```sh
python3 -m pip install -r requirements.txt
```

仅 TXT/JSON 操作无需依赖；PDF 提取需 pypdf、DOCX 需 python-docx、Excel 导入需 openpyxl。扫描 PDF 需宿主 OCR 能力，提取空文本时明确报错。

### Excel 导出

导出器使用 Node.js 与 `@oai/artifact-tool`。在提供该运行时的 Codex/Work 环境，让 Agent 获取运行时路径，并在私有执行目录创建指向该运行时 node_modules 的链接。不要把链接提交到 GitHub。通用环境可在私有导出目录安装兼容版本，导出器已验证版本见 TEST-REPORT；包可用性和宿主权限由运行环境决定。缺少此依赖时仍可输出 JSON；不得声称 Excel 已生成。

```sh
python3 skills/ai-job-match-verification/scripts/jobmatch.py --state private/state.json export-data private/export.json
# 将 export.mjs 复制到可解析 @oai/artifact-tool 的执行目录再运行
node export.mjs private/export.json jobs.xlsx
```

四个工作表：All Jobs、Recommended、Application Tracker、Verification Log。默认 Top10 是静态导出快照；编辑 tracker 后导入、处理冲突，再重新生成推荐。表内筛选不改变持久化状态。

## 使用示例

- “解析这份简历；没写的技能先标 Unknown。”
- “加入这家公司招聘官网；禁用默认猎聘，本地配置优先。”
- “重新核验历史岗位，按最新发布日期排序。”
- “J003 我已拒绝，以后不要再推荐。”
- “这批有300个研发岗位，先提炼最值得确认的技能和方向。”
- “针对这个 JD 给简历优化建议，不改写文件。”
- “导入这份 tracker，列出冲突让我选择。”

正式搜索前必须补齐岗位方向、地点、工作年限、最高学历；同一轮会列出可选的薪资、行业、技能、简历等信息供补充。没有足够经历证据时只判断方向相关性；有证据时用 Met / Unknown / Not Met，并给定性匹配解释。不开匹配百分比。官网必备学历且用户明确不满足可作为硬条件；第三方信息和学历等价经验不得直接排除。

## 测试与开发

```sh
python3 -m unittest discover -s tests -v
python3 install.py --dest /tmp/jobmatch-skills-test
python3 /tmp/jobmatch-skills-test/ai-job-match-verification/scripts/jobmatch.py --state /tmp/jobmatch-test/state.json init
```

[PRD](PRD.md)、[测试报告](TEST-REPORT.md)、[数据契约](skills/ai-job-match-verification/references/data-contract.md)。当前真实示例是2026-10-15的中文官网公开页面观察（UTC为10月14日），不保证之后仍在招；发布日期为空。示例不包含个人简历或用户投递数据。合成案例使用 example.org，不能作为真实职位。

## 持久化与限制

状态 JSON 使用单写入锁和原子替换，文件权限600；状态不保存于安装目录。遇到锁文件先检查是否有任务在运行，勿随意删除。建议备份私人数据。导入只允许已知链接的状态变更，冲突默认保留本地，不从 Excel 导入“核验结论”。

官网关停声明与第三方在招冲突保留两者，官网优先。HTTP 404/403或超时是 Unknown。超过7天的核验在当前视图自动变为 Unverified。7天是 MVP 默认新鲜度，不是招聘有效期承诺。

不自动投递、不集成邮箱/微信、不自动改简历。定时任务需宿主调度工具且用户明确请求；此交付未创建或实跑定时任务，不承诺关机后继续执行。

## GitHub 发布准备

仓库文件已备齐，但本次没有创建远程仓库或公开发布。发布前选择仓库所有者/名称，确认 MIT 许可适合自己的发布计划，检查没有私人数据和运行时链接，运行测试，再推送。不要发布 state.json、原简历、私人导出或访问凭证。添加 CI 的仓库可直接运行 included Python tests。

### 0.1.2 自然语言试用后修复
本轮7种自然语言输入/续聊场景已实跑，首轮缺陷均记录及复测；31项底层回归通过。详见 [行为验收](docs/behavior-tests/REPORT.md)。CLI必要信息门槛、已知能力不重复询问、中文导入导出、官网链接身份去重、来源重放日志幂等已验证。完整简历真实样例有20条线索与137项要求比较；仅1条官网公开招聘，19条仍未知，不宣称全量搜索完成。
推荐表保持紧凑；All Jobs下方有完整要求与证据明细，按J编号关联。四个表名保持稳定，列名与状态默认中文；导入兼容旧英文tracker。导出脚本第四位置参数 `en` 可使用英文显示。

### 0.1.4 来源与推荐规则
优先覆盖阿里系、字节／飞书、Kimi／月之暗面，同时允许搜索其他公司。此偏好通过本地配置启用，不强加给所有安装用户；配置方法见[来源策略](skills/ai-job-match-verification/references/source-policy.md)。本地增删来源覆盖默认来源。

第三方岗位可推荐。发现线索后，按官网入口→ID→名称→关键词→JD职责要求反查；没有找到官网对应职位时保留第三方链接，并明确招聘状态待核实。疑似对应不得自动合并；404不代表岗位关闭。此规则替代0.1.3的官网确认限定。

当前35项回归通过。本次更新未重新开展全量真实岗位搜索；历史样例的招聘状态没有因更新而变为已核实。详见[本次验证](docs/source-policy-update.md)。
