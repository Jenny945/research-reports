# 晶振校准中的 Coefficient 研究报告

## 执行摘要

在晶振校准语境中，"coefficiency" 并非标准术语，应理解为 "coefficient"（系数）的误用或非标准变体。晶振校准中的系数是指描述频率偏差与外部因素（温度、电压、老化等）之间关系的数学参数，通过多点测量数据拟合得出。以温度补偿为例，AT-cut 石英晶体的频率-温度特性遵循三次多项式模型，其系数通过在多个精确温度点测量频率偏差后经最小二乘法拟合求解，再写入 EEPROM 供补偿引擎实时使用。各类晶振产品（TCXO、DCXO、OCXO、MEMS振荡器）均采用逐颗单独校准的方式确定各自的补偿系数。

## Coefficient 的概念与术语辨析

"coefficiency"一词在英语中是一个极为罕见、近乎废弃的词汇，源自拉丁语 con+efficio，意为"协作、联合效率"，与数学和工程领域标准的"coefficient"（系数）是完全不同的两个词。经对 SiTime、Epson、NDK、Vectron、Abracon 等主流晶振厂商文档、IEEE 论文和 3GPP 标准的全面检索，未找到"coefficiency"在晶振技术文献中的任何使用。因此，在晶振校准上下文中遇到的"coefficiency"应被视为"coefficient"的误用、拼写错误或非英语母语者将"coefficient"与"efficiency"混淆的结果。

晶振频率偏差补偿使用的标准术语是"coefficient"（系数），具体包括四类：温度系数描述频率随温度变化的规律，单位为 ppm/°C；老化系数描述频率随时间漂移的速率，单位为 ppm/天或 ppm/年；电压系数描述电源电压变化对频率的影响，单位为 ppm/V；多项式拟合系数是数学模型中的参数项，如三次多项式的 a0、a1、a2、a3。不同晶振类型对这些系数的依赖程度各异——普通 XO 无补偿，仅依赖初始频率偏差（±20~±100 ppm）；TCXO 通过温度补偿系数将精度提升至 ±0.5~±2.5 ppm；OCXO 通过恒温控制将温度效应最小化，但老化系数仍是长期稳定度的核心制约；DCXO 通过数字调谐系数实现 ±2.5 ppm 的可编程精度。值得注意的是，CCXO（Coefficient Correction Crystal Oscillator，系数校正振荡器）这一术语直接使用了"coefficient"，通过 I²C 接口读取温度传感器数据并利用出厂标定的多项式补偿系数（A0~A3）进行实时频率校正。

## 温度补偿系数的校准原理与方法

温度补偿系数的校准本质上是一个测量驱动的最小二乘拟合过程。AT-cut 石英晶体的频率-温度特性遵循三次曲线，标准公式为 Δf/f = α(T-25) + β(T-25)^2 + χ(T-25)^3，其中 T0=25°C 为参考温度。三个系数的物理含义和典型数值如下：α 为一阶系数（单位 ppm/°C），AT-cut 设计切角 35°15' 附近使 α≈0，实现室温附近的零一阶温度系数；β 为二阶系数（单位 ppm/°C²），在 AT-cut 附近也接近于零，使曲线在拐点附近非常平坦；χ 为三阶系数（单位 ppm/°C³），典型值约 1×10^-4 ppm/°C³，是残余的主导项，决定了宽温范围内的频率偏移量级。未经补偿的 AT-cut 晶体在 -40°C 至 +85°C 范围内频率偏差通常为 ±20~±50 ppm。

校准流程分四步进行。第一步为室温基准校准：将 TCXO 置于 25°C ±0.1°C 恒温环境稳定 24 小时，用高精度频率计（精度需比目标精度高一个数量级）测量实际频率，计算初始偏差并通过调整负载电容或数字寄存器补偿至 ±0.5 ppm 以内。第二步为温度扫描与多点测量：典型校准温度点为 -40°C、-20°C、0°C、25°C、55°C、85°C（5~6 个温度点覆盖全工作范围），每个温度点恒温稳定 15~30 分钟确保热平衡，记录每个点的频率偏差值形成数据集。第三步为多项式拟合求解系数：将测量数据代入三次多项式模型，构建正规方程组通过最小二乘法求解系数。华中科技大学的研究表明，为获得 ±0.6 ppm 的补偿精度（-40°C~105°C），实际需要使用五次多项式 Δf(T) = Σ a_k(T-T0)^k (k=0~5)，函数发生电路产生五次多项式电压，求和电路可对各项系数单独调整。第四步为系数存储与验证：拟合得到的系数写入 TCXO 内部 EEPROM/Flash（每个系数 16~24 位定点数），再次遍历温度点验证补偿效果，确保残余误差不超过目标值。

SiTime MEMS 振荡器采用了不同的校准哲学。其 DualMEMS 架构包含 TempFlat MEMS 谐振器（未补偿频率偏移 < ±60 ppm）和温度传感器谐振器（频率-温度斜率约 ±7 ppm/°C），两者物理间距仅 100 µm，温度分辨率达 30 µK，补偿带宽数百 Hz。TurboCompensation 算法将补偿后频率偏移降至 ≤±1 ppm，核心优势在于两个 MEMS 谐振器的热耦合远优于石英 TCXO 中晶体与分立温度传感器的热耦合。

## 老化系数的校准方法

石英晶体老化遵循两种主要数学模型。对数老化模型（Mattuschka 经验模型）为 Δf(t) = A·ln(B·t+1)，适用于初期快速老化阶段——通电初期因污染物脱附和应力释放频率变化较快，随后逐渐趋缓。线性老化模型为 Δf(t) = k·t，适用于经过充分预老化后进入稳定阶段的情况，老化率 k 趋于恒定。Arrhenius 加速老化模型 k = k0·e^(-Ea/(kB·T)) 用于通过高温加速测试外推常温老化率，MIL-PRF-55310 标准规定在 70°C 下进行 30 天老化测试，将数据拟合到数学模型预测长期（10 年）老化性能。

老化系数的校准步骤包括：出厂前在高温（85°C~125°C）下连续运行 7~30 天进行预老化（Burn-in）加速初期老化；在 70°C 恒温下连续测量频率 30 天，每天记录数据；将 30 天数据分别拟合对数模型和线性模型，外推 1 年和 10 年老化值；将老化预测系数写入 EEPROM，系统据此进行长期频率补偿。不同产品的老化率差异显著：标准 XO 首年老化率 ±1~±5 ppm，TCXO 为 ±0.2~±1 ppm，高端 OCXO（SC-cut，冷焊封装）首年 ±0.01~±0.1 ppm，后续年老化率可降至 ≤±0.01 ppm。

## 电压系数与 DCXO 数字补偿

电压系数描述电源电压变化对振荡频率的影响，公式为 Vc = (Δf/f0)/ΔVDD，单位 ppm/V。机理为电源电压变化引起振荡电路偏置点变化、负载电容等效值变化、进而频率偏移。校准方法是在 25°C 下测量 VDD 在额定电压 ±5% 三个点的频率，计算 ppm/V 灵敏度系数。SiTime MEMS VCXO 的 Kv（频率-电压斜率）变化率 <1%，而石英 VCXO 的 Kv 在整个控制电压范围内变化 10~20%。

DCXO 数字补偿引擎的工作原理为：片上温度传感器以 ≥100 Hz 带宽采样温度；根据当前温度定位到对应系数区间；计算补偿值 Δf_comp = a0 + a1·ΔT + a2·ΔT² + a3·ΔT³；将补偿值转换为数字调谐字写入频率调整寄存器；寄存器控制开关电容阵列或变容二极管阵列改变负载电容，实时微调频率。DCXO 内部 EEPROM 中存储的数据结构包括校准标识和校验和、温度断点表、多项式系数组（每个区间 16~24 位定点数）、老化系数和电压系数。

## 手机通信系统中的系数校准实践

在 5G 手机中，晶振校准系数与 AFC（自动频率控制）机制紧密关联。Qualcomm 平台采用三次多项式模型 f(t) = C3·(t-t0)^3 + C2·(t-t0)^2 + C1·(t-t0) + C0，其中 t0 通常取 30°C。C0 通过粗校准确定——遍历 PMIC 内部电容阵列找到使频偏在 ±2 ppm 内的电容值；C1 通过精校准确定——让设备持续高功率工作发热使温度上升 ≥0.5°C，测量频率变化后计算线性斜率；C2 近似为零在量产中不校准；C3 量级约 10^-5 ppm/°C³ 仅极限温度修正时使用。MTK 平台采用更简单的线性模型：频率偏差 = Slope×DAC + Offset，通过设定两个不同 DAC 值测量频率误差计算斜率和初始 DAC 值，写入 NV 存储。两种平台均逐台设备单独校准，因为 PCB 布局、PMIC 供电特性和热环境各不相同。

3GPP TS 38.101 规定 UE 调制载波频率误差必须在 ±0.1 ppm 以内（相对于基站载波频率，1 ms 测量间隔），对 2.0 GHz 载波这意味着频率误差不超过 ±200 Hz。频率误差过大直接导致 CRC 错误增多、掉话和链路中断。AFC 在手机运行期间持续工作：测量基站下行信号频率、与自身晶振频率比较计算实时误差、根据存储的系数计算 DAC 调整量、更新 DAC 值使手机频率与基站同步。

## 生产校准流程与设备要求

晶振出厂校准的典型流程为：频率初调（通过激光微调或离子溅射调节电极质量使频率进入 ±10 ppm 范围）；温度补偿校准（TCXO/DTCXO 在温箱中测试多个温度点拟合补偿曲线）；系数写入（补偿系数写入片上 NVM）；最终测试（ESR 测试、频率漂移测试、温度循环测试、老化筛选 1000 小时以上）；100% 出厂检测（每颗逐一通过频率精度复测和气密性抽检）。所有 TCXO/DTCXO/OCXO 和手机 DCXO 均采用逐颗单独校准，因为每颗晶体的切角、厚度、电极质量的微小差异导致频率-温度特性各不相同。

校准设备要求包括：频率计数器精度需比目标精度高十倍（如校准 ±0.5 ppm 则需 ≤±0.05 ppm，推荐 Keysight 53230A 或同等）；恒温箱温度范围 -40°C~+105°C、稳定性 ±0.1°C、均匀性 ±0.5°C；可编程直流电源电压波动 < ±1%、分辨率 1 mV；数据采集系统支持 GPIB/USB/LAN 接口自动化记录。实验室环境使用 10~20 个温度点、2~4 小时单颗校准时间、目标精度 ±0.1~±0.5 ppm；量产环境使用 ATE 自动化校准，5~8 个温度点、30 秒~2 分钟单颗校准时间、目标精度 ±0.5~±2 ppm、良率 ≥99.5%。

## 综合分析

晶振校准系数的确定本质上是一个从物理测量到数学建模的系统工程过程。从方法论角度，三次/五次多项式拟合模型的选择体现了精度与复杂度的权衡——三次模型足以覆盖大多数 AT-cut 晶体的频率-温度特性（±0.5~±2 ppm 精度），而五次模型为极端温度范围和超高精度场景（±0.1~±0.6 ppm）提供更精细的修正。最小二乘法作为拟合算法，在正规方程组的框架下保证了系数的最优性，但对温度点选择策略和测量精度有严格要求。

从产品实现角度，补偿系数经历了从纯模拟（热敏电阻网络）到半数字（查找表+DAC）再到全集成 MEMS（DualMEMS+TurboCompensation）的演进。模拟方案受限于热敏电阻精度和响应带宽（5~10 Hz），数字方案突破了带宽限制但受 ADC/DAC 精度约束，MEMS 方案通过芯片级热耦合实现了数百 Hz 补偿带宽和 30 µK 温度分辨率。在 5G 手机中，Qualcomm 的三次多项式和 MTK 的线性模型代表了两种主流 AFC 策略，核心目标均是满足 3GPP ±0.1 ppm 的 UE 频率精度要求。

从校准经济学角度，逐颗单独校准是所有温度补偿型晶振的必需做法，因为每颗晶体的物理参数微差导致其系数各异。量产中通过 ATE 自动化将单颗校准时间压缩到 30 秒~2 分钟，但代价是精度从实验室的 ±0.1 ppm 放宽到 ±0.5~±2 ppm。校准系数一旦写入 NVM 即成为该器件的"数字指纹"，决定了其全寿命周期的频率补偿性能，因此校准数据的完整性和可靠性至关重要。

## 结论

晶振校准中的"coefficiency"实质上是"coefficient"（系数）的非标准表述，指描述频率偏差与温度、电压、老化等外部因素关系的数学参数。温度补偿系数通过多点温度测量（典型 5~6 个温度点）和三次/五次多项式最小二乘拟合求解得出，写入 EEPROM 供补偿引擎实时使用。老化系数通过加速老化测试配合对数/线性模型外推获得。电压系数通过额定电压 ±5% 范围内的三点测量确定。所有温度补偿型晶振均采用逐颗单独校准。在 5G 手机中，Qualcomm 的 C0/C1/C3 三次多项式模型和 MTK 的 Slope-DAC 线性模型是主流 AFC 校准策略，目标满足 3GPP TS 38.101 规定的 ±0.1 ppm UE 频率精度要求。SiTime MEMS 振荡器通过 DualMEMS 架构实现了芯片级热耦合和 ≤±1 ppm 的补偿性能，代表了数字补偿系数实现的最新方向。

## 参考资料

1. [Coefficiency - The Free Dictionary](https://www.thefreedictionary.com/Coefficiency)
2. [Coefficient - Merriam-Webster Dictionary](https://www.merriam-webster.com/dictionary/coefficient)
3. [TCXO Tutorial - Microchip Technology](https://ww1.microchip.com/downloads/aemDocuments/documents/VOP/ApplicationNotes/ApplicationNotes/TCXO+Tutorial.pdf)
4. [AN10020 Definitions of VCXO Specifications - SiTime](https://www.sitime.com/support/resource-library/application-notes/an10020-definitions-vcxo-specifications)
5. [Basic Knowledge of Crystal Unit - Epson](https://www.epsondevice.com/crystal/cn/techinfo/column/crystal-unit/)
6. [AT和BT切石英晶体频率温度特性随切角变化关系研究 - 百度文库](https://wenku.baidu.com/view/36007e1d01020740be1e650e52ea551810a6c96f.html)
7. [一款高精度宽温度范围TCXO芯片的设计 - 空间期刊](https://mc.spacejournal.cn/article/id/7fa2ebda-4ac7-4b4a-91fc-328048e1f4d8)
8. [TCXO，高精度温补晶振是如何产生的 - 知乎](https://zhuanlan.zhihu.com/p/643245154)
9. [晶振温度系数补偿技术 - 电子工程专辑](https://www.eet-china.com/mp/a452235.html)
10. [AFC校准原理详解 (Qualcomm + MTK) - CSDN](https://blog.csdn.net/shigzhu/article/details/126053675)
11. [XO校准：频率误差控制详解 - CSDN](https://blog.csdn.net/qq_39543984/article/details/123062364)
12. [手机MTK平台校准原理 - 电子工程专辑](https://www.eet-china.com/mp/a472997.html)
13. [SiTime DualMEMS与TurboCompensation技术](https://sitimechina.com/support/application/dualmems-and-turbocompensation-temperature-sensing)
14. [SiTime Elite Super-TCXO深入分析](https://sitimechina.com/support/application/elite-super-tcxo-overview)
15. [OCXO Aging Correction Methods - BRIDZA](https://rf.bridza.com/resources/qanda/ocxo-aging-correction-methods.html)
16. [OCXO与TCXO老化性能 - SiTime China](https://www.sitimechina.com/support/docs/ocxo-tcxo-aging-performance-surpass-quartz-crystal)
17. [CCXO系数校正振荡器 - CSDN](https://blog.csdn.net/weixin_30181209/article/details/162243064)
18. [DCXO数字控制晶振 - CSDN](https://blog.csdn.net/weixin_29174013/article/details/162322479)
19. [Mitigating Crystal Oscillator Aging Effects - Microwaves & RF](https://www.mwrf.com/technologies/components/article/55316380/q-tech-corp-mitigating-the-effects-of-crystal-oscillator-aging)
20. [3GPP TS 38.101-1: NR UE Radio Transmission and Reception](https://www.etsi.org/deliver/etsi_ts/138100_138199/13810101/17.18.00_60/ts_13810101v171800p.pdf)
21. [Crystal Oscillator Application Notes - Q-Tech](https://www.q-tech.com/wp-content/uploads/QTAN104-Crystal-Oscillator-Application-Notes.pdf)
22. [SiTime新款MEMS振荡器助力AI数据中心](https://www.eet-china.com/mp/a495871.html)
23. [TCXO Types: ADTCXO, DTCXO, DCXO, MCXO - RF Wireless World](https://www.rfwireless-world.com/terminology/tcxo-types-adtcxo-dtcxo-dcxo-mcxo)
24. [理解SC cut晶体的温度系数 - Dynamic Engineers](https://www.dynamicengineers.com.cn/article_info.asp?id=141175)
