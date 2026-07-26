# FFT SNR 测试中 4-tone 波形的技术原理分析

FFT SNR 测试中是否"一定要"使用 4-tone 波形，需要从 ADC/DAC 动态参数测试的基本原理出发来理解。SNR（信噪比）定义为信号 RMS 功率与噪声 RMS 功率之比（不含谐波和 DC），理想 N 位 ADC 的满量程正弦波理论 SNR 为 6.02N+1.76 dB。IEEE 1241 标准和 ADI AN-835 应用笔记规定的标准 SNR 测试方法使用单音正弦波，信号电平设在满量程以下 0.1~1 dB，通过相干采样（f_analog = N_cycles × f_encode / N_samples，且 N_cycles 取质数）避免频谱泄漏，对采集的 16k~64k 点做 FFT，在频域中排除前 6 次谐波和 DC 后积分噪声功率。因此，对于纯粹的 SNR 测量，单音正弦波已经足够——因为 SNR 本质上衡量的是 ADC 的量化噪声和热噪声水平，这些噪声在奈奎斯特带宽内近似白噪声，单音激励已能充分激励量化器并测出噪声底。

那么为什么会出现 4-tone 测试？核心原因在于单音测试的局限性。ADI 明确指出："单音谐波失真测量对于了解 ADC 线性度的一般情况是有用的，但此类数据不能直接用于预测独立输入音之间的互调性能。"当需要同时评估宽带性能、互调失真和真实通信信号场景下的 SNR 时，单音测试不够用，需要多音信号。而 4-tone 是多音测试家族中的一个工程折中选择——并非"一定要"用 4-tone，而是在带宽覆盖、峰均比可控性和互调产物可分辨性三者之间取得了优于其他音数的平衡点。

## 4-tone 波形的构造与峰均比特性

4-tone 信号是 4 个等幅正弦波的叠加：x(t) = Σ A·sin(2π·f_k·t + φ_k)（k=1~4）。频率选择遵循相干采样原则——各频率对齐到 DFT bin 中心频率（通常取奇数 bin），且各音之间留有间隔作为互调失真产物的观测窗口。

峰均比（PAPR/Crest Factor）是理解"为什么是 4 tone"的关键。等幅多音信号的 PAPR 随音数 N 近似以 √N 增长。对于 4 个等幅同相音，最坏情况峰值为 4A、RMS 为 2A，PAPR 高达 6.02 dB。但通过 Newman 相位或 Schroeder 相位优化，可将 4-tone 的 PAPR 降至约 3~4 dB，接近单音的 3.01 dB。相比之下，16-tone 即使优化后 PAPR 仍达 8~10 dB，而 2-tone 的 PAPR 仅 3 dB 但带宽覆盖不足。4-tone 在带宽覆盖和 PAPR 之间取得了良好的折中——既能覆盖足够带宽，又不会因 PAPR 过高导致信号平均功率远低于满量程而劣化 SNR 测量精度。

PAPR 对 SNR 测量的影响机制是这样的：高 PAPR 信号需要将峰值限制在 ADC 满量程以下以避免削波，这迫使平均信号电平降低，从而降低有效信噪比。SNR 损失约等于 PAPR_signal 减去 PAPR_sine（相对于单音测试的退化量）。4-tone 经相位优化后 PAPR 仅约 3~4 dB，SNR 损失可控；而 16-tone 即使优化后 PAPR 仍达 8~10 dB，SNR 损失显著。这就是为什么不用更多音的原因——音数越多带宽覆盖越好，但 PAPR 急剧上升导致 SNR 测量精度下降。

## 为什么恰好是 4 而非 2 或 8

从带宽覆盖角度，2-tone 仅测试两个频率点及其互调产物（2f1±f2、2f2±f1 等），无法评估宽带内的噪声和失真分布。4-tone 覆盖 4 个频率点，产生的互调产物更密集，能更好地反映宽带性能。从 PAPR 角度，8-tone 和 16-tone 虽然带宽覆盖更好，但 PAPR 显著增大（即使优化相位也难低于 7~9 dB），导致 ADC 工作点远离满量程，SNR 测量精度下降。从互调产物结构角度，4 个音产生的二阶和三阶互调产物数量约 20 个，分布在频带内各处，既能充分暴露非线性问题，又不会像多音（如 64-tone）那样使产物互相重叠难以分辨。4-tone 恰好处于这个 sweet spot。

从模拟真实信号角度，实际通信信号（OFDM、WCDMA 等）是多载波宽带信号，4-tone 能比单音更好地近似这种宽带特性，同时保持测试的可分析性。Keysight N7621B 软件支持最多 4097 音的多音测试，IMD 抑制大于 70 dBc，但实际工程中常用 4~12 音作为折中。4-tone 可视为 NPR（噪声功率比）测试的简化版本——NPR 用数千个音模拟高斯噪声并加陷波来测试噪声底，4-tone 适合产线快速测试。

## 应用场景

在通信系统 SNR 测试中，5G NR 和 WiFi 的 OFDM 信号本质是多载波，4-tone 模拟其 PAPR 特性来评估 ADC 在真实负载下的 SNR 表现。在互调失真测试中，2-tone 测 IMD 是标准做法，4-tone 进一步暴露高阶互调和交叉调制。在 DOCSIS 3.1 宽带 cable modem 系统中，要求 ADC 在整个频段（最高约 1.8 GHz）内保持线性度，多音测试用于评估满载条件下的性能。在频谱平坦度测试中，IEEE 802.11 要求发射信号频谱平坦度在特定范围内，多音信号可用于验证通带内平坦度。

从数学原理角度，多音信号的功率谱密度在 4 个频率处集中能量，其余频点为"空白区"可用于观测噪声和失真产物。相干采样条件下各音频率为 DFT bin 的整数倍，无需加窗即可避免泄漏；若非相干则需使用 Blackman-Harris 窗，但会牺牲频率分辨率。4-tone 信号的总功率在各音间均分，每音功率比单音低 6 dB（4 音等分），这使得单音幅度低于满量程，但通过相位优化保持峰值接近满量程，从而最大化 SNR 测量动态范围。

## 综合分析

4-tone 并非 SNR 测试的强制要求，IEEE 1241 标准的基准 SNR 测试方法仍是单音正弦波 FFT 法。4-tone 是在需要评估宽带性能、互调失真以及模拟真实多载波通信信号时的工程折中选择。选择 4 而非 2 或 8 的核心理由是三重平衡：相比 2-tone，4-tone 提供了更宽的带宽覆盖和更密集的互调产物分布，能更好地暴露宽带非线性问题；相比 8/16-tone，4-tone 经相位优化后 PAPR 仅约 3~4 dB，接近单音水平，不会因峰均比过高导致平均信号电平大幅降低而劣化 SNR 测量精度；4 个音产生的约 20 个互调产物数量适中，既能充分激励非线性又不会互相重叠难以分辨。

如果测试目标仅是纯粹的 SNR 指标，单音正弦波完全足够。如果需要同时评估 SNR、IMD 和宽带线性度，或者需要模拟 OFDM 等真实多载波信号场景，4-tone 是合理的选择。如果"一定要用 4-tone"的说法出现在某个具体的产品规范或测试规范中，更可能是因为该产品的应用场景（如通信系统 ADC）需要在多载波条件下评估动态性能，而非 4-tone 是 SNR 测试的通用必需条件。

## 结论

FFT SNR 测试中 4-tone 波形并非通用强制要求，而是在特定场景下的工程最优选择。对于纯 SNR 测量，IEEE 1241 标准规定的单音正弦波 FFT 法是基准方法。4-tone 的价值在于它能在带宽覆盖、PAPR 可控性和互调产物可分辨性三者间取得最佳平衡——相比 2-tone 带宽更宽、相比 8/16-tone 峰均比更低，且互调产物结构适中便于分析。4-tone 经相位优化后 PAPR 约 3~4 dB 接近单音水平，SNR 测量损失可控，同时能模拟 OFDM 等真实通信信号的宽带多载波特性，适用于需要同时评估 SNR、互调失真和宽带线性度的通信系统 ADC/DAC 测试场景。

## 参考资料

1. [AN-835: Understanding High Speed ADC Testing and Evaluation - Analog Devices](https://www.analog.com/en/resources/app-notes/an-835.html)
2. [MT-003: Understand SINAD, ENOB, SNR, THD, THD+N, and SFDR - Analog Devices](https://www.analog.com/media/en/training-seminars/tutorials/MT-003.pdf)
3. [MT-005: Noise Power Ratio (NPR) - Analog Devices](https://www.analog.com/media/en/training-seminars/tutorials/MT-005.pdf)
4. [IEEE Std 1241-2010 - IEEE Standard for ADC Terminology and Test Methods](https://ieeexplore.ieee.org/document/5692956)
5. [IEEE Std 1241-2023 - IEEE Standard for ADC Terminology and Test Methods](https://ieeexplore.ieee.org/document/10269815)
6. [multitone - Generate sparse multitone signal - MATLAB MathWorks](https://www.mathworks.com/help/audio/ref/multitone.html)
7. [Boyd, S. (1986) - Multitone Signals with Low Crest Factor - Stanford](https://www-leland.stanford.edu/~boyd/papers/multitone_low_crest.html)
8. [Boyd (1986) - IEEE Xplore](https://ieeexplore.ieee.org/document/634697)
9. [N7621B Signal Studio for Multitone Distortion - Keysight](https://www.keysight.com.cn/cn/zh/assets/7018-04111/technical-overviews/5991-3194.pdf)
10. [SBAA002A: Dynamic Tests For A/D Converter Performance - TI](https://www.ti.com/lit/an/sbaa002a/sbaa002a.pdf)
11. [DOCSIS 3.1 Component Tests - Rohde & Schwarz](https://cdn.rohde-schwarz.com.cn/pws/dl_downloads/dl_application/application_notes/1ma285___docsis_3_1_component_tests/1MA285_3e_DOCSIS_3.1_Component_Tests.pdf)
12. [Defining and Testing Dynamic Parameters in High-Speed ADCs - Analog Devices](https://www.analog.com/en/resources/technical-articles/defining-and-testing-dynamic-parameters-in-highspeed-adcs-part-1.html)
13. [How Does Signal Crest Factor Influence SNR - DSP StackExchange](https://dsp.stackexchange.com/questions/94849/how-does-signal-crest-factor-influence-snr-and-effective-resolution-in-adcs)
14. [ADC学习 频谱性能指标 - CSDN](https://blog.csdn.net/qq_41019681/article/details/118834032)
15. [Analysis and Design of Multi-Tone Signal Generation Algorithms - IEEE](https://ieeexplore.ieee.org/document/9301549)
