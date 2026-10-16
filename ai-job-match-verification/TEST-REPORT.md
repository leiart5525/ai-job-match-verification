# 测试报告
当前0.1.2以 [自然语言行为验收报告](docs/behavior-tests/REPORT.md) 为准，包含首轮失败、修复及实际复试。31项Python回归通过；7种自然语言输入/续聊场景实跑。真实网络核验与市场覆盖限制没有隐藏。Skill YAML使用系统Ruby解析与名称/字段/引用检查；bundled quick_validate.py缺PyYAML且网络安装失败，未虚报其通过。调度和其他宿主未验证。

当前0.1.4补充验证见[来源策略更新](docs/source-policy-update.md)：35项回归通过。0.1.3的官网确认推荐限定已撤销；保留历史测试记录供追溯，不能作为当前规则。
