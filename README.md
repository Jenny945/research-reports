# 研究报告与云端工作同步仓库

本仓库同步了 CodeBuddy 云端工作环境的所有工作成果，包括研究报告、技能配置、研究计划、PDF 生成脚本和会话数据。

## 目录结构

```
├── research_report_*.md / .pdf    # 4 份技术研究报告（Markdown + PDF）
├── skills/                        # CodeBuddy 技能配置
│   ├── automation-task-manager/   # 自动化任务管理器（定时任务）
│   ├── github-connector/          # GitHub 连接器
│   ├── preview/                   # 预览技能
│   └── README.md                  # 技能说明
├── research-plans/                # 研究计划文件
├── pdf-scripts/                   # PDF 生成脚本（Python + reportlab）
├── session-data/                  # 云端会话记录
│   ├── *.jsonl                    # 主会话记录
│   ├── subagents/                 # 子代理运行记录
│   └── tool-results/              # 工具调用结果
└── README.md                      # 本文件
```

## 研究报告清单

1. **UL MIMO TPMI 技术研究** - 5G NR 上行 MIMO 传输预编码矩阵指示
2. **晶振校准中的 Coefficient 研究** - 晶振频率补偿系数的校准方法
3. **FFT SNR 4-tone 波形分析** - ADC/DAC 测试中多音信号的使用原理
4. **码本传输、相干性与 TPMI 标记详解** - 基于 codebook 的 PUSCH 传输、R1T0/R1T2/R2T0 标记含义

## 自动化任务管理器

`skills/automation-task-manager/` 目录包含 CodeBuddy 的自动化定时任务技能：
- `SKILL.md` - 技能定义和使用说明
- `references/cron_examples.md` - Cron 表达式示例
- `scripts/scheduler-api.sh` - 调度器 API 脚本

## 同步方法

云端生成新内容后：
```bash
git add -A
git commit -m "描述新增内容"
git push
```

本地电脑获取最新内容：
```bash
git pull
```
