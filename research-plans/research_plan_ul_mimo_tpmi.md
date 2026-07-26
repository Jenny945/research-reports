# UL MIMO TPMI 研究计划

## 研究主题
UL MIMO TPMI（Uplink MIMO Transmit Precoding Matrix Indicator，上行 MIMO 传输预编码矩阵指示）

## 查询类型分析
这是一个**深度优先查询**（Depth-first query）。UL MIMO TPMI 是 5G NR 上行 MIMO 中的单一核心技术主题，需要从多个角度深入分析：
- 技术原理与标准定义
- 预编码矩阵设计
- DCI 信令与控制机制
- 码本子集约束
- 性能与实际应用

## 研究子任务分解

### 子任务 1：TPMI 技术原理与 3GPP 标准定义
- TPMI 的定义、目的与基本概念
- 3GPP TS 38.211/38.212/38.214 中的相关标准定义
- 上行预编码的基本原理（基于码本的预编码）
- TPMI 与 SRI（Sounding Reference Resource Indicator）的关系
- 非 codebook based 和 codebook based 上行传输的区别

### 子任务 2：TPMI 码本设计与预编码矩阵
- 上行码本设计（rank 1, rank 2 等）
- TPMI 指示的预编码矩阵结构
- 不同天线端口数下的码本（2 port, 4 port）
- 码本子集约束（Codebook Subset Restriction）
- 下行控制信息 DCI 0_1 中的 TPMI 字段

### 子任务 3：TPMI 信令流程与实际应用
- DCI 0_1 中 TPMI 字段的编解码
- gNB 如何选择 TPMI（基于 SRS 测量）
- UE 如何应用 TPMI 进行上行预编码
- 与 SRS、PMI 的交互
- 实际网络中的性能考虑与优化

## 信息检索策略
- 使用 WebSearch 搜索 3GPP 标准、技术文档
- 使用 wechat-article-search 搜索中文技术文章（微信公众号是高质量的中文技术信息源）
- 使用 WebFetch 获取 3GPP 标准、ShareTechnote、3GPP spec 等权威来源

## 搜索关键词
- 英文: "UL MIMO TPMI", "5G NR uplink precoding TPMI", "3GPP TPMI codebook", "DCI 0_1 TPMI field"
- 中文: "上行MIMO TPMI", "5G上行预编码", "TPMI码本", "DCI0_1 TPMI"
- 时间范围: 2022-2026（获取最新的标准版本和分析）

## 输出格式
深度技术分析报告，约 2000-3000 字，包含：
- 报告标题
- 执行摘要
- 技术背景
- 核心技术分析（多个章节）
- 综合分析
- 结论
- 参考资料
