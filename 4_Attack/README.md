# 4_Attack

## 攻击方法调研

- [分类、数学公式与详细实现流程](ATTACK_METHODS_zh.md)：优先追溯现有防御评测中的攻击，覆盖 NN/MRP、权重与逐 token VMA、IMA/SIP、ISA/DEML、梯度反演、统计解密及多模态恢复。
- [论文、官方代码核验与复现入口](ATTACK_PAPERS_AND_CODE.md)：区分原始实现、场景适配、数据仓库和未核实代码。
- [可运行的 NumPy 基础实现](attack_baselines_numpy.py)：`python 4_Attack/attack_baselines_numpy.py --self-check`；合成数据验证，不代表 LLM 实验复现。

## 原有 PDF

提出隐私重建攻击的论文。PIDI / ADMI 同时包含防御，因此在 Embedding/Training 也保存相同 PDF。

[返回总 README](../README.md) · [逐篇分类依据](../research_notes/PAPER_CLASSIFICATION.md)

- [PIDI / ADMI](From_Prompts_to_Responses_Dual-Sided_Data_Leakage_and_Defense_in_Split_Large_Language_Models.pdf) · [背景、方法与配图](../README.md#paper-15)
- [RASR](Inverting_the_Hidden_Unveiling_Multimodal_Privacy_Leakage_in_Collaborative_LVLM_Inference.pdf) · [背景、方法与配图](../README.md#paper-16)
