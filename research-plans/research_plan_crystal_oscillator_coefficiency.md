# 晶振校准中 Coefficiency 研究计划

## 研究主题
晶振（Crystal Oscillator）校准中的 coefficiency 概念——它是什么、如何校准得出、在晶振频率补偿中的作用。

## 查询类型分析
这是一个**深度优先查询**。核心问题围绕"coefficiency"这一单一概念，需要从多个角度深入分析：
- 术语定义与含义（什么是 coefficiency）
- 不同类型晶振（TCXO、OCXO、DCXO、VCXO）中的补偿系数
- 校准方法与流程（如何通过测量和拟合得出）
- 数学模型（温度补偿曲线、老化补偿模型）
- 实际应用与产品实现

## 研究子任务分解

### 子任务 1：Coefficiency 概念与术语定义
- 确认 "coefficiency" 在晶振校准中的确切含义
- 与常见术语 "coefficient" 的关系和区别
- 晶振频率偏差的补偿系数类型（温度系数、老化系数、电压系数）
- 不同晶振类型中的补偿系数应用

### 子任务 2：Coefficiency 的校准方法与数学模型
- 温度补偿系数的校准流程（AT-cut 晶体的频率-温度特性）
- 三次/五次多项式拟合模型
- 校准设备与测量环境
- 老化系数的校准方法
- 电压系数（voltage coefficient）的校准
- 数字补偿（DCXO）中的系数生成方法

### 子任务 3：实际产品与应用
- TCXO/DCXO/OCXO 产品中的 coefficiency 实现
- SiTime、Epson、NDK 等厂商的实现方法
- MEMS 振荡器中的数字补偿系数
- 5G/通信系统中晶振校准的应用

## 信息检索策略
- 使用 WebSearch 搜索英文和中文关键词
- 使用 wechat-article-search 搜索微信公众号技术文章
- 使用 WebFetch 获取技术文档和白皮书

## 搜索关键词
- 英文: "crystal oscillator calibration coefficient", "TCXO temperature compensation coefficient", "OCXO frequency coefficient calibration", "DCXO digital compensation polynomial", "crystal oscillator coefficiency"
- 中文: "晶振校准 系数", "TCXO 温度补偿系数", "晶振频率补偿 coefficiency", "晶体振荡器 校准系数 曲线拟合"
- 时间范围: 近3年（2023-2026）

## 输出格式
深度技术分析报告，约 1500-3000 字，包含：
- 报告标题
- 核心概念定义
- 技术原理分析
- 校准方法详解
- 数学模型
- 综合分析
- 结论
- 参考资料

最终输出为 PDF 文档（参照之前 UL MIMO TPMI 的 PDF 生成方式）
