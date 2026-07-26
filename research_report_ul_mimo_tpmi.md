# 5G NR 上行 MIMO 中的 TPMI 技术研究

## 执行摘要

TPMI（Transmit Precoding Matrix Indicator，传输预编码矩阵指示）是 5G NR 上行 MIMO 中基于码本（codebook-based）PUSCH 传输的核心预编码指示机制。gNB 通过测量 UE 发送的 SRS 信号获取上行信道状态，从 3GPP 预定义的码本表中选择最优预编码矩阵，并通过 DCI Format 0_1 中的"Precoding information and number of layers"字段将 TPMI 索引和传输层数联合指示给 UE。TPMI 与 SRI 协同工作——SRI 选定波束/天线面板方向，TPMI 确定预编码矩阵和层数。码本设计覆盖 2 端口和 4 端口场景，并受 UE 相干传输能力约束通过 codebookSubset 参数进行子集限制，在预编码灵活性与信令开销间取得平衡。

## 技术背景

在 5G NR 上行 MIMO 传输中，当 UE 配备多根发射天线时，需要将数据层（layer）映射到多个天线端口上。不同的预编码矩阵会产生不同的空间波束方向和增益。3GPP 定义了两种上行预编码方案：基于码本（codebook-based）和非码本（non-codebook-based）传输，由 RRC 参数 `txConfig` 配置。TPMI 仅在 codebook-based 方案中使用，由 gNB 统一决策预编码矩阵——这利用了基站侧更强的计算能力和通过 SRS 测量获得的更准确的上行信道状态信息。这与下行 MIMO 中 UE 通过 CSI 上报 PMI 的机制形成对称关系：下行由 UE 推荐 PMI，上行由 gNB 指示 TPMI。

两种上行预编码方案的核心差异如下：codebook-based 方案中预编码矩阵从 3GPP 预定义码本表中选取，gNB 通过 TPMI 指示，SRS 资源配置多端口（1/2/4 port），最多 2 个 SRS 资源，TDD 和 FDD 均适用，不依赖信道互易性；non-codebook-based 方案中 UE 基于 CSI-RS 下行测量自行计算预编码矩阵，DCI 仅携带 SRI 而无 TPMI 字段，SRS 仅单端口，最多 4 个 SRS 资源，必须存在上下行信道互易性，仅适用于 TDD 模式。

## 核心技术分析

### 一、TPMI 的标准定义与码本表结构

TPMI 相关的预编码矩阵定义在 3GPP TS 38.211 Section 6.3.1.5 中，预编码矩阵 W 的维度为天线端口数 × 层数。其选择取决于三个关键参数：层数、天线端口数和是否启用变换预编码（transform precoding）。标准定义了 7 张核心码本表覆盖 2 端口和 4 端口场景。

码本表选择机制具体为：1 天线端口单层传输时 W=1（无需 TPMI）；1 层 2 端口传输对应 Table 6.3.1.5-1；1 层 4 端口在变换预编码启用时对应 Table 6.3.1.5-2，禁用时对应 Table 6.3.1.5-3；2 层 2 端口对应 Table 6.3.1.5-4；2 层 4 端口对应 Table 6.3.1.5-5；3 层 4 端口对应 Table 6.3.1.5-6；4 层 4 端口对应 Table 6.3.1.5-7。Release 18 进一步扩展支持 8 天线端口，TPMI 取值范围扩展至 0–304。

值得注意的是，变换预编码（DFT-s-OFDM 波形）仅支持单层传输，因此 rank ≥ 2 的码本表仅在变换预编码禁用（CP-OFDM 波形）时定义。4 端口单层传输在启用/禁用变换预编码时使用不同的码本表，因为码本设计需适配 DFT-s-OFDM 波形的低 PAPR 特性。

### 二、2 端口码本设计

2 天线端口单层传输（Table 6.3.1.5-1）共定义 6 个 TPMI，预编码向量为 2×1 矩阵。其中 TPMI 0 对应 [1, 0]ᵀ，TPMI 1 对应 [0, 1]ᵀ，均为非相干码本（单端口发送）；TPMI 2 至 5 分别对应 [1,1]ᵀ/√2、[1,-1]ᵀ/√2、[1,j]ᵀ/√2、[1,-j]ᵀ/√2，为完全相干码本（两端口等幅发送，仅相位不同）。

2 天线端口双层传输（Table 6.3.1.5-4）仅定义 1 个 TPMI，预编码矩阵为 (1/√2)×[[1,0],[0,1]]，即归一化单位矩阵，两端口分别承载独立数据流，属于非相干传输。

### 三、4 端口码本设计与相干能力分层

4 天线端口单层传输（变换预编码禁用，Table 6.3.1.5-3）共定义 28 个 TPMI（TPMI 0-27），预编码向量为 4×1 矩阵，码本按相干能力分层。TPMI 0-3 为非相干码本，每次仅一个端口发送，如 [1,0,0,0]ᵀ、[0,1,0,0]ᵀ 等；TPMI 4-11 为部分相干码本，两个端口同时发送，涵盖端口对 {0,1}、{2,3}、{0,2}、{1,3} 的组合，如 [1,1,0,0]ᵀ/√2、[1,−1,0,0]ᵀ/√2、[1,j,0,0]ᵀ/√2 等；TPMI 12-27 为完全相干码本，四个端口同时发送，利用 QPSK 相位组合，形如 [1,1,1,1]ᵀ/2、[1,−1,1,−1]ᵀ/2、[1,j,−1,−j]ᵀ/2 等。

4 天线端口双层传输（Table 6.3.1.5-5）定义多个 TPMI，预编码矩阵为 4×2，同样按相干能力分层。以 MATLAB 文档示例为例，4 天线端口、2 层、TPMI=7 时的预编码矩阵 W 为 (1/2)×[[1,0,1,0],[0,1,0,1]]ᵀ，该矩阵将 layer 0 映射到天线端口 0 和 2（等幅同相），layer 1 映射到天线端口 1 和 3，属于部分相干传输模式。

### 四、码本子集约束机制

码本子集约束通过高层参数 `codebookSubset`（在 PUSCH-Config 中配置）限制 UE 可用的 TPMI 范围，从而减少 gNB 的预编码器搜索复杂度。三种子集类型为：`fullyAndPartialAndNonCoherent` 允许全部 TPMI（完全+部分+非相干均可）；`partialAndNonCoherent` 允许部分相干和非相干码本，排除完全相干码本；`nonCoherent` 仅允许非相干码本，为最严格约束。

UE 通过 `MIMO-ParametersPerBand` 信元中的 `pusch-TransCoherence` 上报上行相干传输能力，以频段为单位。fullCoherent 表示所有天线端口可相干传输，可用全部码字；partialCoherent 表示同一相干组内（2 端口）可相干，可用部分相干+非相干码字；nonCoherent 表示无端口可相干，仅可用非相干码字。配置规则为：UE 上报 partialAndNonCoherent 时 gNB 不应配置 fullyAndPartialAndNonCoherent；UE 上报 nonCoherent 时只能配置 nonCoherent；当 nrofSRS-Ports=2 且 usage=codebook 时，codebookSubset 不能设为 partialAndNonCoherent（2 端口只区分全相干和非相干）；若 UE 未上报相干能力，默认为非相干。以 2 端口、maxRank=2、nonCoherent 配置为例，Rank 1 仅 TPMI 0 和 1 可用（单端口发送），Rank 2 仅 TPMI 0 可用（单位矩阵）。

### 五、DCI 0_1 中的 TPMI 信令

DCI Format 0_1 中与上行预编码直接相关的字段有三个，形成级联依赖关系。SRI（SRS Resource Indicator）指示 gNB 测量的 SRS 资源，用于确定波束/天线面板方向；"Precoding information and number of layers"为联合编码字段，指示预编码矩阵索引和传输层数；Antenna ports 指示 DMRS 天线端口分配，须与 TPMI 指示的层数一致。

TPMI 字段的比特数由 TS 38.212 中定义的映射表决定，取决于天线端口数（nrofSRS-Ports：1/2/4）、变换预编码状态、maxRank 和 codebookSubset 的组合。当 txConfig=nonCodebook 时该字段为 0 bit。典型配置下，4 端口 maxRank=4 时约需 5-6 bit，2 端口 maxRank=2 时约需 3-4 bit。codebookSubset 配置为 nonCoherent 时，全相干和部分相干码字被排除，TPMI 可选值减少，信令开销降低。

### 六、完整信令流程与 gNB/UE 处理过程

完整的 TPMI 信令流程贯穿 UE 能力上报、RRC 配置、SRS 测量、DCI 指示和 PUSCH 预编码应用全链条。

在 UE 能力上报阶段，UE 上报相干能力（pusch-TransCoherence）和满功率模式（ul-FullPwrMode）。gNB 据此配置 usage=codebook 的 SRS Resource Set（最多 2 个 SRS Resource，每个 SRS 配置相同端口数 2 或 4），以及 codebookSubset 和 maxRank 等参数。

在 SRS 测量与预编码选择阶段，UE 在配置的 SRS 资源上发送 SRS，gNB 接收并进行信道估计获得上行信道矩阵 H。gNB 基于信道测量结果，结合 UE 相干能力和 maxRank 限制，在可用码本子集中搜索最优预编码矩阵，选择准则通常基于最大化上行容量或 SINR。当配置多个 SRS 资源时，gNB 选择最优 SRS 资源（对应不同波束方向或天线面板）并通过 SRI 指示。在 TDD 系统中，gNB 还可利用信道互易性从 SRS 估计的上行信道推断下行信道状态。

在 DCI 指示与 UE 应用阶段，gNB 通过 PDCCH 发送 DCI 0_1，包含 SRI、TPMI+层数、天线端口等字段。UE 解析 DCI 后，根据 txConfig、nrofSRS-Ports、transformPrecoder、maxRank、codebookSubset 等 RRC 参数选择对应的 TS 38.212 码本映射表，将"Precoding information and number of layers"的码点映射为具体 TPMI 索引和传输层数。随后根据 TPMI 索引在 TS 38.211 的预编码矩阵表中查找具体的预编码矩阵 W，使用 SRI 指示的 SRS 资源对应的波束/天线端口应用 W 矩阵对传输层进行空间映射。

### 七、实际网络中的性能考虑

gNB 的预编码选择通常基于以下准则：最大化容量（遍历码本子集选择使上行容量最大的 TPMI）、最大化 SINR（在干扰受限场景下选择使信号干扰噪声比最优的预编码）、以及通过 codebookSubset 限制减少搜索空间降低计算复杂度。

在上行 MU-MIMO 中，gNB 从多个 UE 接收 SRS 估计各 UE 上行信道，基于用户配对算法选择空间兼容的 UE 组，为每个配对 UE 选择合适 TPMI 最小化用户间干扰。DMRS 端口分配通过"CDM groups without data"指示实现多 UE 正交复用，支持最多 12 层 MU-MIMO。TPMI 与 MCS 的选择密切相关——gNB 在选择 TPMI 时同时评估不同预编码矩阵下的信道质量，更高 rank 配合合适预编码可支持更高 MCS。此外，DCI 中 2 比特的 SRS request 字段可触发非周期 SRS 传输，为后续 TPMI 选择更新信道信息。

### 八、Rank-TPMI 组合标记（R1T0 与 R1T2）

在工程实践和测试调试中，常用 `RxTy` 格式的速记标记来简洁表示 Rank 与 TPMI 的组合配置，其中 R 代表 Rank（秩/传输层数），T 代表 TPMI 索引值。例如 R1T0 表示 Rank 1（单层传输）且 TPMI index = 0，R1T2 表示 Rank 1（单层传输）且 TPMI index = 2。这种标记法并非 3GPP 标准中的正式定义，而是常见于研发测试报告、测试仪器配置界面和工程师技术交流中的非正式速记法。

以 2 天线端口、单层传输（Table 6.3.1.5-1）为例，R1T0 与 R1T2 代表两种截然不同的传输模式。R1T0 对应 TPMI 0，预编码向量为 [1, 0]ᵀ，即仅使用天线端口 0 发射、端口 1 不发射，属于非相干（non-coherent）传输，UE 仅通过单根天线发送上行信号。R1T2 对应 TPMI 2，预编码向量为 [1, 1]ᵀ/√2，即两根天线端口等幅同相同时发射，属于完全相干（fully coherent）传输，两端口协同发射实现发射分集增益。

两者的核心区别在于发射功率和分集特性。R1T0 仅用单端口发射，发射功率受限于单天线最大功率；R1T2 用双端口协同发射，总发射功率可在两端口间分配，理论上可获得约 3dB 的分集增益。这一区别与上行满功率发送（UL Full Power Transmission）机制密切相关——在 nonCoherent 码本子集约束下仅允许类似 R1T0 的单端口码本（TPMI 0 和 1），而 fullCoherent 能力下才允许类似 R1T2 的多端口相干码本（TPMI 2-5）。需要将此标记与 SRS 天线切换中的 "1T2R"/"2T4R" 标记（格式为数字在前，T 代表发射天线数、R 代表接收天线数）区分开。

## 综合分析

TPMI 机制的设计体现了 5G NR 在灵活性与复杂度之间的精细平衡。从码本设计角度，3GPP 通过相干能力分层（non-coherent/partial-coherent/full-coherent）使码本结构匹配 UE 实际硬件能力——相干能力较弱的 UE 无需支持复杂的全相干预编码，降低了射频链路要求；而相干能力强的 UE 可利用全相干码本获得更高的空间复用增益。codebookSubset 机制进一步将这一匹配关系动态化，gNB 可根据 UE 能力上报和实际信道条件灵活配置可用码本范围。

从信令效率角度，TPMI 与层数的联合编码设计减少了 DCI 开销。codebookSubset 为 nonCoherent 时信令比特数显著降低，这对上行控制信道资源紧张的场景尤为有利。2 端口和 4 端口采用不同比特宽度的映射表，也体现了按需分配信令资源的原则。

从系统性能角度，gNB 基于 SRS 测量的集中式预编码决策比 UE 自主决策具有信道信息优势，尤其在 FDD 模式下 non-codebook 方案不可用时，codebook-based 方案配合 TPMI 成为上行 MIMO 的唯一选择。但在 TDD 模式下，non-codebook 方案利用信道互易性可支持更多 SRS 资源（4 个），在多 panel 场景下提供更灵活的波束选择，两种方案各有优势。

## 结论

TPMI 是 5G NR 上行 MIMO 码本传输模式的核心预编码指示机制，通过 gNB 基于 SRS 测量的集中式预编码决策实现上行空间复用增益。其技术体系涵盖 3GPP TS 38.211 定义的预编码矩阵码本表（支持 2/4 端口、Rank 1-4 传输）、TS 38.212 定义的 DCI 0_1 联合编码字段、以及 TS 38.214 定义的物理层过程。TPMI 与 SRI 协同工作——SRI 选定波束/天线面板方向，TPMI 确定预编码矩阵和层数——共同完成上行空间传输方案配置。码本子集约束机制通过 codebookSubset 参数将可用码本范围与 UE 相干传输能力匹配，在预编码灵活性与信令开销间取得平衡。该机制支持从单层非相干到四层全相干的多样化上行 MIMO 传输，适用于 TDD 和 FDD 两种双工模式，是 5G NR 上行 MIMO 性能的关键技术支撑。

## 参考资料

1. [ShareTechnote - 5G PUSCH Transmission Mode](https://www.sharetechnote.com/html/5G/5G_PUSCH_TxMode.html)
2. [ShareTechnote - 5G DCI Format](https://www.sharetechnote.com/html/5G/5G_DCI.html)
3. [ShareTechnote - 5G PUSCH](https://www.sharetechnote.com/html/5G/5G_PUSCH.html)
4. [3GLTEInfo - 5G NR Precoding and Codebooks](https://www.3glteinfo.com/5g/protocols/phy/precoding-and-codebooks/)
5. [MATLAB - nrPUSCHCodebook Documentation](https://www.mathworks.com/help/5g/ref/nrpuschcodebook.html)
6. [MATLAB - nrPUSCH Documentation](https://www.mathworks.com/help/5g/ref/nrpusch.html)
7. [简书 - 关于NR PUSCH Codebook based MIMO的认识](https://www.jianshu.com/p/91c07c7564dd)
8. [CSDN - 5G NR基于码本的上行传输](https://blog.csdn.net/LinkEverything/article/details/131255013)
9. [CSDN - 5G NR协议学习系列：Uplink传输机制](https://blog.csdn.net/u014496800/article/details/145748552)
10. [知乎 - NR PUSCH 相干传输](https://zhuanlan.zhihu.com/p/623523338)
11. [3GPP Portal - Specification 38.214](https://portal.3gpp.org/desktopmodules/Specifications/SpecificationDetails.aspx?specificationId=3216)
12. [ETSI - TS 138 211 (3GPP TS 38.211)](https://www.etsi.org/deliver/etsi_ts/138200_138299/138211/17.01.00_60/ts_138211v170100p.pdf)
13. [ETSI - TS 138 212 (3GPP TS 38.212)](https://www.etsi.org/deliver/etsi_ts/138200_138299/138212/15.02.00_60/ts_138212v150200p.pdf)
14. [ETSI - TS 138 214 V18.7.0 (3GPP TS 38.214)](https://www.etsi.org/deliver/etsi_ts/138200_138299/138214/18.07.00_60/ts_138214v180700p.pdf)
15. [arXiv - Precoding Matrix Indicator in the 5G NR Protocol](https://arxiv.org/html/2601.05092v1)
16. [CSDN - 5G NR 之上行满功率发送](https://blog.csdn.net/LinkEverything/article/details/124975679)
17. [知乎 - SRS 天线切换中 1T2R 1T4R 和 2T4R 的解释](https://zhuanlan.zhihu.com/p/2023114347250028559)
18. [ETSI - TS 138 508-1 UE 一致性测试通用测试环境](https://www.etsi.org/deliver/etsi_ts/138500_138599/13850801/18.07.00_60/ts_13850801v180700p.pdf)
