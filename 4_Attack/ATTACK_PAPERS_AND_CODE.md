# 攻击论文与代码索引

核验日期：2026-11-12。配合[分类、公式与实现笔记](ATTACK_METHODS_zh.md)阅读。优先级来自本地防御论文的实际引用或评测，不表示统一的攻击强弱排名。以下链接指向论文原站、作者仓库或作者 artifact；“未核实代码”表示本次未确认到可用的独立实现，不等于证明作者从未发布。

本轮额外阅读全文 17 篇，缓存位于被 Git 忽略的 `research_notes/extracted/attack_review/`，不计入根目录原有的 20 篇 / 24 份 PDF。补充论文通过原文链接访问；本地原有 PIDI、RASR 的 PDF 保留在本目录。

## 1. 首先看哪些论文

| 优先阅读路线 | 原因 | 对应笔记 |
|---|---|---|
| TWIST → AloePri 附录 D.1 → Hidden No More / EDNN / InvBERT / ISA | 分清权重映射恢复、逐 token 搜索、学习式反演和连续优化；AloePri 提供同路线实验细节 | [几何与模型变换](ATTACK_METHODS_zh.md#a-weight-vma)、[序列搜索](ATTACK_METHODS_zh.md#a-seq-vma)、[IMA](ATTACK_METHODS_zh.md#a-ima) |
| SnD / SGT / OSNIP → NN / MRP / BeamClean | 最直接的词向量恢复基线，以及利用语言先验改进加噪表示恢复 | [NN/MRP](ATTACK_METHODS_zh.md#a-nn)、[BeamClean](ATTACK_METHODS_zh.md#a-beamclean) |
| Privacy Adapters → Luo 等 / Qu 等 | 查询驱动的 token 分类与已知模型优化攻击 | [A1/A2/A3](ATTACK_METHODS_zh.md#a-luo)、[DEML](ATTACK_METHODS_zh.md#a-deml) |
| DualGuard / PrivPair → BiSR → TAG / LAMP | 首先理解切分点梯度及未知尾部，再回看原始参数梯度攻击 | [梯度攻击](ATTACK_METHODS_zh.md#gradients) |
| PIDI/ADMI → SIP / MC → PIDI | 推理期同时利用两端状态与生成历史，不要求真实训练梯度 | [输出端](ATTACK_METHODS_zh.md#a-mc)、[PIDI](ATTACK_METHODS_zh.md#a-pidi) |
| COVERT / RASR → ISA / CapRecover | 区分图像像素重建、文本恢复、图像语义泄漏 | [多模态](ATTACK_METHODS_zh.md#multimodal) |

## 2. 论文索引与原文定位

“定位”以论文中的章节/算法为主，避免混淆 arXiv 与会议版本的 PDF 页码。本地防御 PDF 的物理页码见主笔记 §2.1。

| 编号 | 论文、年份及原文 | 核心攻击 / 阅读位置 | 与当前论文库的关系 |
|---|---|---|---|
| R01 | [Hidden No More: Attacking and Defending Private Third-Party LLM Inference](https://proceedings.mlr.press/v267/thomas25b.html)，ICML 2025 | 因果前缀逐 token 匹配；§4–5、Algorithm 1、Appendix E；私有 embedding 扩展见 Appendix I | TWIST 的相关 VMA 来源；OSNIP 使用逐 token 版本。不要把其 Algorithm 1 与全部权重匹配适配视作同一实现 |
| R02 | [An Inversion Attack Against Obfuscated Embedding Matrix in Language Model Inference](https://aclanthology.org/2024.emnlp-main.126/)，EMNLP 2024 | EDNN：坐标差分消去论文所针对的加性混淆，再做词向量匹配；§3 | TWIST/AloePri 引用的不变量攻击基础；COVERT 也讨论它 |
| R03 | [InvBERT: Reconstructing Text from Contextualized Word Embeddings by Inverting the BERT Pipeline](https://arxiv.org/abs/2109.10104)，2021 初稿，JCLS 2023 | InvBERT Classify 与 Seq2Seq；§3–4 | TWIST 的 IMA 引用；AloePri 的 Qwen2 小解码器是后续适配配置 |
| R04 | [Depth Gives a False Sense of Privacy: LLM Internal States Inversion](https://www.usenix.org/conference/usenixsecurity25/presentation/dong-tian)，USENIX Security 2025 | ISA：ER、TBS、黑盒替代前缀；§4、Algorithm 1 | TWIST/AloePri/COVERT 引用；COVERT 的视觉评测属于场景适配 |
| R05 | [Prompt Inversion Attack against Collaborative Inference of Large Language Models](https://arxiv.org/abs/2503.09022)，IEEE S&P 2025 | PIA / DEML：连续表示优化、范围/词表约束、语义候选与激活校准；§5 | Privacy Adapters 的优化攻击基线 |
| R06 | [Prompt Inference Attack on Distributed Large Language Model Inference Frameworks](https://arxiv.org/abs/2503.09291)，CCS 2025 | A1 同分布分类；A2 合成补齐词表；A3 有限查询、锚点、自训练与 beam；§4、Algorithms 1–3 | Privacy Adapters 的分类攻击来源；原文 6 层 MLP 与其 4 层适配不同 |
| R07 | [Unveiling the Vulnerability of Private Fine-Tuning in Split-Based Frameworks for Large Language Models: A Bidirectionally Enhanced Attack](https://arxiv.org/abs/2409.00960)，CCS 2024 | SIP、NaMoE、BiSR；§3–4 | DualGuard / PrivPair / PIDI 的重要共同参考；前向与反向增强分别需要对应观测 |
| R08 | [TAG: Gradient Attack on Transformer-based Language Models](https://aclanthology.org/2021.findings-emnlp.305/)，Findings of EMNLP 2021 | 通过 L2/L1 组合匹配模型参数梯度；方法部分 | DualGuard / PrivPair 使用分割适配；切分点梯度版本与原算法的未知量不同 |
| R09 | [LAMP: Extracting Text from Gradients with Language Model Priors](https://openreview.net/forum?id=6iqd9JAVR1z)，NeurIPS 2022；[全文](https://arxiv.org/abs/2202.08827) | 连续梯度匹配与离散词序搜索交替；§4、Algorithm 1 | 同上；原分类实验中已知标签，分割生成任务未必满足 |
| R10 | [Deep Leakage from Gradients](https://arxiv.org/abs/1906.08935)，NeurIPS 2019 | DLG：同时优化 dummy 输入与标签，使参数梯度一致；方法部分 | TAG/LAMP 的基础；补充阅读 |
| R11 | [Text Embeddings Reveal (Almost) As Much As Text](https://aclanthology.org/2023.emnlp-main.765/)，EMNLP 2023 | Vec2Text：基础反演 → 重嵌入 → 迭代纠正；§3 | 句向量反演代表作；是扩展接口，不能直接等同于 token hidden-state 攻击 |
| R12 | [Transferable Embedding Inversion Attack: Uncovering Privacy Risks in Text Embeddings without Model Queries](https://aclanthology.org/2024.acl-long.230/)，ACL 2024 | TEIA：少量泄露配对、几何/对抗对齐、迁移解码；§3 | PrivTune 引用；“无查询”仍有泄露配对，不是纯 NN |
| R13 | [DeepInvert: Semi-Supervised Embedding Inversion Against Obfuscated Language Models](https://arxiv.org/abs/2608.04477)，2026 预印本 | shadow 监督 + 真实无标签日志、EMA、一致性、分阶段训练；§4–5 | 较新补充，不声称现有防御均已被独立复现攻破 |
| R14 | [Can Sequence-to-Sequence Models Crack Substitution Ciphers?](https://aclanthology.org/2021.acl-long.561/)，ACL 2021 | 频率排名编码 + seq2seq 解密；§3 | TWIST/AloePri 的 SDA 来源；原始字符替换任务迁移到 LLM token 需适配 |
| R15 | [BeamClean: Language Aware Embedding Reconstruction](https://arxiv.org/abs/2505.13758)，2025 预印本 | 噪声模型估计与语言先验 beam 重建；§4、Algorithm 1 | SGT 评测引用；不需目标深层权重，但需要正确 embedding 空间 |
| R16 | [Information Leakage in Embedding Models](https://arxiv.org/abs/2004.00053)，CCS 2020 | embedding 反演、属性及成员泄漏；重点 §4 等攻击部分 | 基础参考；支持理解 SnD/PrivTune 涉及的重建与属性推断 |
| R17 | [CapRecover: A Cross-Modality Feature Inversion Attack Framework on Vision Language Models](https://arxiv.org/abs/2507.22828)，ACM MM 2025 | 中间视觉特征 → Q-Former/对齐 → caption/label；§3 | COVERT 参考；恢复语义而非图像像素 |
| R18 | [From Prompts to Responses: Dual-Sided Data Leakage and Defense in Split Large Language Models](https://proceedings.mlr.press/v306/gu26o.html)，2026；[本地 PDF](From_Prompts_to_Responses_Dual-Sided_Data_Leakage_and_Defense_in_Split_Large_Language_Models.pdf) | PIDI / ADMI；§4、§5，重点 patch-wise 联合输入/响应反演 | 原库已有；PIDI 是推理期攻击 |
| R19 | [Inverting the Hidden: Unveiling Multimodal Privacy Leakage in Collaborative LVLM Inference，本地 PDF](Inverting_the_Hidden_Unveiling_Multimodal_Privacy_Leakage_in_Collaborative_LVLM_Inference.pdf) | RASR：分支初始重建 + 原模型一致性精修；§V，PDF 第 5–6 页 | 原库已有；文本与图像的恢复目标分别评测 |

扩展目标：梯度属性推断可看 [Melis 等，Exploiting Unintended Feature Leakage in Collaborative Learning，S&P 2019](https://arxiv.org/abs/1805.04049)；成员推断可看 [Shokri 等，Membership Inference Attacks Against Machine Learning Models，S&P 2017](https://arxiv.org/abs/1610.05820)；训练数据抽取可看 [Carlini 等，Extracting Training Data from Large Language Models，USENIX Security 2021](https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting)。这三篇作为扩展引用，本轮没有将它们计入额外阅读全文的 17 篇。

<a id="code-status"></a>
## 3. 官方代码核验与入口

“已读取”表示检查了目录及关键源文件，**不表示已经装环境、训练或复现论文指标**。下面 GitHub 文件链接固定到本轮检查的 commit；仓库首页可以用来查看后续更新。权重、数据和依赖是否仍可下载，仍须在实际复现时确认。

| 方法 | 官方入口及核验结果 | 优先阅读文件 / 使用注意 |
|---|---|---|
| EDNN | ACL Anthology 的[作者 software.zip](https://aclanthology.org/attachments/2024.emnlp-main.126.software.zip)，已下载并读取 | 包内 `ednn_attack/ednn.py`、`run.sh`；核心 matching 不需要原 key，脚本中的 key 用于构造/验证对应关系 |
| ISA | [Zenodo artifact v2](https://doi.org/10.5281/zenodo.15605325)，已下载并读取 | `white-box-inversion/attack_batch.py`；`black-box-inversion/replication/replicate.py`、`inversion.py`、`inference.py`。先检查 `--attack`、目标层、steps/lr、`--tbs-changevar`、`--w-dm`；v2 不含全部预训练结果 |
| DEML | [ygZhou02/DEML](https://github.com/ygZhou02/DEML)，已读取 | [`invert.py`](https://github.com/ygZhou02/DEML/blob/d09512e64028924e5e7fa47f4aabc424db280680/invert.py)：`get_hidden_state`、`invert_embedding`、`invert_and_find_best`、`main`；启动脚本 `run_inversion.sh`。公开代码的主要约束代理与论文式 (13) 有区别，见主笔记 §5.2 |
| SIP / NaMoE / BiSR | [StupidTrees/SplitLLM](https://github.com/StupidTrees/SplitLLM)，已读取 | [`inversion_models.py`](https://github.com/StupidTrees/SplitLLM/blob/c376590227f9718077765824af4088665bb78687/sfl/model/attacker/sip/inversion_models.py)、[`inversion_training.py`](https://github.com/StupidTrees/SplitLLM/blob/c376590227f9718077765824af4088665bb78687/sfl/model/attacker/sip/inversion_training.py)、[`sip_attacker.py`](https://github.com/StupidTrees/SplitLLM/blob/c376590227f9718077765824af4088665bb78687/sfl/model/attacker/sip/sip_attacker.py)；前向增强见 [`sma_attacker.py`](https://github.com/StupidTrees/SplitLLM/blob/c376590227f9718077765824af4088665bb78687/sfl/model/attacker/sma_attacker.py) |
| 切分点 TAG / LAMP | 同一 [SplitLLM](https://github.com/StupidTrees/SplitLLM) 中的适配实现，已读取 | [`dlg_attacker.py`](https://github.com/StupidTrees/SplitLLM/blob/c376590227f9718077765824af4088665bb78687/sfl/model/attacker/dlg_attacker.py)：`TAGAttacker`、`LAMPAttacker`、`_gma_loss`；观测为激活梯度，不能当作原始全参数梯度攻击逐字复现 |
| 原始 LAMP 及其 TAG/DLG 基线 | [eth-sri/lamp](https://github.com/eth-sri/lamp)，已读取 | [`attack.py`](https://github.com/eth-sri/lamp/blob/3128022ce4e3732d2dad82eca60a80c22cbab450/attack.py)、`lamp_cos.sh`、`lamp_l1l2.sh`、`tag.sh`、`dlg.sh`。TAG 原作者独立仓库本轮未确认；这里的 TAG 是 LAMP 作者实现的基线 |
| DLG | [mit-han-lab/dlg](https://github.com/mit-han-lab/dlg)，已读取 | [`main.py`](https://github.com/mit-han-lab/dlg/blob/d21007fa1540ba2303ebc034976aa331814727c7/main.py)。是经典梯度匹配示例，迁移到现代 LLM 仍需任务、词嵌入和 loss 适配 |
| Vec2Text | [jxmorris12/vec2text](https://github.com/jxmorris12/vec2text)，已读取 | [`api.py`](https://github.com/jxmorris12/vec2text/blob/abe48a565f5d4fb1814b0cbfb2cb230b5d9ff6b6/vec2text/api.py)、[`corrector_encoder.py`](https://github.com/jxmorris12/vec2text/blob/abe48a565f5d4fb1814b0cbfb2cb230b5d9ff6b6/vec2text/models/corrector_encoder.py)、[`trainers/corrector.py`](https://github.com/jxmorris12/vec2text/blob/abe48a565f5d4fb1814b0cbfb2cb230b5d9ff6b6/vec2text/trainers/corrector.py)。检查目标 embedder 与 checkpoint 是否匹配 |
| TEIA | [coffree0123/TEIA](https://github.com/coffree0123/TEIA)，已读取；README 提示迁移尚未完成 | [`research/model/adv_attack_model.py`](https://github.com/coffree0123/TEIA/blob/e38ce989b1ac1551660f20d7cb62722449ab1cbd/research/model/adv_attack_model.py)、`main.py`、`research/config/base_config.py`。存在源代码不表示当前环境可直接一键运行 |
| SDA | [NadaAldarrab/s2s-decipherment](https://github.com/NadaAldarrab/s2s-decipherment)，已核对完整文件树 | 截至 commit `bc6997b7687cdd0d1c8bb7819e1e38bf22ecc08a` 只有 README 与 `gutenberg-data.zip`；**这是数据入口，没有完整训练/推断代码** |
| CapRecover | [Jus1mple/Image2CaptionAttack](https://github.com/Jus1mple/Image2CaptionAttack)，已读取 | [`feature_mappers.py`](https://github.com/Jus1mple/Image2CaptionAttack/blob/c022c77a38d813686a0afd1a6b0488cb83f1b200/src/models/feature_mappers.py)、[`qformer_opt.py`](https://github.com/Jus1mple/Image2CaptionAttack/blob/c022c77a38d813686a0afd1a6b0488cb83f1b200/src/models/qformer_opt.py)、[`trainer.py`](https://github.com/Jus1mple/Image2CaptionAttack/blob/c022c77a38d813686a0afd1a6b0488cb83f1b200/src/core/trainer.py) |
| PIDI / MC | 论文给出 [FLAIR-THU/VFLAIR-LLM](https://github.com/FLAIR-THU/VFLAIR-LLM)，已检查当前默认分支目录及相关通用实现 | [`ModelCompletion_LLM.py`](https://github.com/FLAIR-THU/VFLAIR-LLM/blob/ff18565d89dce6367b6f13881a415c053b60cb0f/src/evaluates/attacks/ModelCompletion_LLM.py)、[`VanillaModelInversion_WhiteBox.py`](https://github.com/FLAIR-THU/VFLAIR-LLM/blob/ff18565d89dce6367b6f13881a415c053b60cb0f/src/evaluates/attacks/VanillaModelInversion_WhiteBox.py) 是相关框架文件；**本次未定位到独立 PIDI / patch-wise 实现，不能声称这两个文件就是完整 PIDI** |
| Hidden No More 的 VMA | 论文给出的 [`ritual-net/vma-external`](https://github.com/ritual-net/vma-external) 本轮网页及 GitHub API 检查均返回 404 | 按论文 Algorithm 1 / Appendix E 阅读；404 可能与迁移、权限或下线有关，本次无法从该入口获取代码 |
| InvBERT | 论文给出[匿名评审仓库](https://anonymous.4open.science/r/invbert-BF31) | 未核实到可用正式发布仓库；按 Classify / Seq2Seq 两条路径实现，不能将其他 IMA 的配置称作作者配置 |
| Luo 等 A1/A2/A3、DeepInvert、BeamClean、RASR、TWIST/AloePri 权重 VMA/IA | 本轮未确认到这些具体算法可用的独立官方实现入口 | 主笔记提供公式、原文定位和实现流程；有数值基础函数的部分见下一节。不能以相关框架存在代替方法代码核验 |

## 4. 本仓库的基础实现及如何运行

[`attack_baselines_numpy.py`](attack_baselines_numpy.py) 是本轮独立编写的教学参考，不是复制作者代码，也不替代学习式攻击的训练脚本。依赖 Python 3.10+ 与 NumPy。

```bash
python -m pip install numpy
python 4_Attack/attack_baselines_numpy.py --self-check
```

| 函数 | 作用 | 接口约定 |
|---|---|---|
| `nearest_rows` | 分块精确 L2/cosine Top-k；用于 NN/KNN | 返回 `(观测行数, k)` 的候选行号与距离；L2 返回平方距离 |
| `nth_neighbor` | SGT MRP 所用的第 r 邻居基础操作 | rank 从 1 开始、按从近到远排序；不是通用的“最远邻攻击” |
| `coordinate_difference`、`ednn_mapping` | EDNN 坐标差分匹配 | 每个词向量加同一个标量时差分不变；不对任意旋转成立 |
| `sorted_row_mapping`、`majority_mapping` | 特征置换下的排序行匹配、多层投票 | 映射方向为“观测行 → 原行”；独立 NN 不强制全局双射 |
| `gate_fingerprint` | 跨层 row-mean 指纹 | 传入已构造好的投影表；真实 checkpoint 的变换相消由调用者核对 |
| `attention_fingerprint` | 满列秩投影表的二次型不变量 | 用线性方程求解；一般可逆变换下成立，加噪后不保证精确一致 |
| `frequency_rank_mapping` | TFMA 的频率排名匹配 | 两侧计数同长度；相同频率按稳定次序破平，需要单独分析歧义 |
| `greedy_prefix_match` | 逐 token 前缀搜索及特征/序列置换变体 | 模型通过 `forward_last(prefix_ids)` 回调提供；默认遍历全词表；返回 token、匹配行号与距离 |
| `labels_from_logit_gradient` | hard-label CE 的直接 logits 梯度标签恢复 | 仅适用函数文档的无权重、单 hard-label 条件；不是任意隐藏层梯度攻击 |

本轮 `--self-check` 的 12 组检查均通过：NN、MRP 特例、EDNN 加性不变量及旋转边界、权重行列映射、多层投票、Gate 指纹、Attention 一般可逆不变量及加噪边界、频率映射、因果前缀与置换变体、logits 梯度标签识别。测试数据为合成矩阵和小型因果回调，**没有实际加载 LLM、训练反演器或测量论文恢复率**。

## 5. 复现时建议保存的最小配置

```yaml
victim:
  checkpoint: "公开基座及版本"
  tokenizer: "分词器、chat template、特殊 token"
  split_layers: ["head 终点", "body 终点"]
  client_finetuned: true
observation:
  activation_tensors: ["具体名称、层号与 shape"]
  gradients: "none / cut-point / parameter"
  generation_history: "是否跨步可关联、是否包含真实采样 token"
defense:
  mechanism: "算法与保护位置"
  key_available: false
  key_reused: true
  noise: "分布、幅度、相关性、重采样规则"
attacker:
  model_access: "真实前缀 / 公开基座 / 查询 / 无查询"
  paired_data: "同部署 / shadow / 无"
  labeled_samples: 0
  unlabeled_samples: 0
  query_tokens: 0
  optimizer: "lr、steps、restart、精度"
  candidates: "完整词表或明确的 Top-k/beam"
evaluation:
  split: "按文档或用户独立划分"
  token_accuracy: "全 token 与敏感实体分别报告"
  sentence_exact_match: true
  seeds: [0, 1, 2]
```

这只是记录模板，不是任何论文的默认超参数。具体复现应先复用作者环境与小规模数据跑通，再逐项改变保护机制、可见信息与预算；只比较指标而不对齐这些条件，难以判断防御差异来自哪里。
