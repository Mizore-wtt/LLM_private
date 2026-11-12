# 逐篇分类依据

核对范围：本地 20 篇 PDF（合计 371 页）的摘要、方法与相关训练设置；不是逐页校勘全部实验，也未复现实验。下表页码均是 PDF 物理页码。分类判断与论文声称的安全保证分开，不因“混淆”“加密”等命名就推定已获得密码学安全。

Inference 与 Training 先看保护对象及上传接口，再看原模型是否参与任务适配。只训练新保护模块且原模型冻结，仍归 Inference；基座冻结但训练任务 LoRA/DoRA，归 Training。Prompt 方案即使需要云端适配，也不会仅因有微调被改归 Embedding。

Model 沿用用户图中的“Model+Token 联合变换”含义。DualGuard 等学习式参数变化归 Training；COVERT 同时具备联合重参数化和原视觉模块微调，交叉收录。

| 论文 | 存放目录 | 参数/训练事实 | 正文定位 | 分类理由 |
|---|---|---|---|---|
| [COVERT](../3_Model/COVERT_Privacy-Preserving_Covariant_Obfuscation_for_VLMaaS_via_Exact_Reparameterization_and_Tailored_Tuning.pdf) | `3_Model`；`2_Embedding/Training` | 微调原视觉编码器首个 ViT 块的注意力矩阵及前置归一化层；部分其余参数冻结。 | §4.1–4.3，PDF 第 6–9 页，尤其第 8 页 Tailored Parameter Tuning。 | 联合变换数据与模型权重属于 Model；同时确实微调原视觉特征提取模块，因此交叉收录 Training。不是只训练外围混淆器。 |
| [AloePri](../3_Model/Towards_Privacy-Preserving_LLM_Inference_via_Covariant_Obfuscation.pdf) | `3_Model` | 离线代数变换模型权重；核心流程不是用任务数据梯度微调原模型。 | §4–5，PDF 第 4–11 页；第 7 页 Overview 与图 2。 | 关键是模型与 token 的配套变换。虽然包含 token 置换，也不把这个不可分的联合机制单独当作 Prompt 替换方法。 |
| [TWIST](../3_Model/TWIST_Private_Tenant-Dedicated_LLM_Serving_via_Joint_Model-Token_Transformation.pdf) | `3_Model` | 离线变换和扰动权重；不以训练任务适配器作为核心保护步骤。 | §3–4，PDF 第 3–8 页；第 5 页图 1 与算法 1。 | Model+Token 联合保护；不因其在线发生在推理阶段就归入 Embedding/Inference。 |
| [SplitLoRA](../2_Embedding/Training/SplitLoRA_A_Split_Parameter-Efficient_Fine-Tuning_Framework_for_Large_Language_Models.pdf) | `2_Embedding/Training` | 在客户端和服务器训练 LoRA，改变模型的有效权重。 | §III，PDF 第 3–5 页；第 4 页明确发送激活及对应标签并更新 LoRA。 | 作为训练侧表示传输的基础框架归入 Training，并标记“框架”。原文 vanilla 切分还传标签；不能将其概括成输入输出都不出端或已防反演。 |
| [U-SplitDoRA](../2_Embedding/Training/U-SplitDoRA_An_Improved_Privacy-Preserved_U-Shaped_Split_Parameter-Efficient_Fine-Tuning_Framework_Through_Weight_Decomposition_for_Large_Language_Models.pdf) | `2_Embedding/Training` | 训练 DoRA 的幅值向量和低秩方向参数，改变模型的有效权重。 | §3.1–3.5，PDF 第 5–9 页；第 6 页图 2、第 8 页 DoRA 和 U-shaped architecture。 | 训练框架通过切分控制原始输入和标签的直接暴露，未把额外混淆器作为核心；仍属于 Training 的框架子类。 |
| [DualGuard](../2_Embedding/Training/DualGuard_A_Parameter_Space_Transformation_Approach_for_Bidirectional_Defense_in_Split-Based_LLM_Fine-Tuning.pdf) | `2_Embedding/Training` | 本地预热修改原首尾模型；正式阶段冻结头部，继续训练中间与尾部。 | §3.1–3.3，PDF 第 3–5 页；第 4 页图 2。 | 参数空间变化由训练得到，核心是训练式表示保护；不同于 TWIST/AloePri 的配套代数重参数化，故不只凭标题中的 Parameter Space 放入 Model。 |
| [PrivTune](../2_Embedding/Training/PrivTune_Efficient_and_Privacy-Preserving_Fine-Tuning_of_Large_Language_Models_via_Device-Cloud_Collaboration.pdf) | `2_Embedding/Training` | 云端训练 LoRA；客户端产生并扰动中间表示。 | §IV–V，PDF 第 3–6 页；第 5 页 Collaborative Training Stage 与图 1。 | 尽管扰动在前向传播时执行，论文的完整方法仍包含云端任务微调，因此归入 Training。 |
| [FedSEA-LLaMA](../2_Embedding/Training/FedSEA-LLaMA_A_Secure_Efficient_and_Adaptive_Federated_Splitting_Framework_for_Large_Language_Models.pdf) | `2_Embedding/Training` | 使用联邦分割 LoRA 微调；噪声同时服务训练及后续推理。 | Model / Privacy Preservation，PDF 第 3–5 页；第 4 页明确选择前向隐藏状态加噪而非直接梯度加噪。 | 按完整流程归入 Training。论文也加速推理，但没有因此将其等同于 SnD 那种无需任务微调的冻结原模型方法。 |
| [PrivPair](../2_Embedding/Training/Privacy-Preserving_Split_Learning_for_Federated_LLM_Fine-Tuning.pdf) | `2_Embedding/Training` | 服务器中间模型 B 冻结；客户端原头部 A、尾部 C 及成对适配器参与训练。 | §IV-B、§V-A–C，PDF 第 4–6 页；第 4 页明确 B frozen and updates only A and C，第 5 页恢复器与 STE。 | 中间大模型冻结不代表整套原模型冻结，客户端首尾仍微调，符合用户举例的 Training。 |
| [Privacy Adapters](../2_Embedding/Inference/Defense_Against_Prompt_Inversion_Attacks_An_Information-Theoretic_Approach_for_LLM_Collaborative_Inference.pdf) | `2_Embedding/Inference` | 原 Transformer 和云端层全程冻结；仅训练新插入的隐私适配器与训练用攻击器。 | §2.1、§3.2–3.3、§5，PDF 第 2–6 页，尤其第 5 页 All transformer layers remain frozen。 | 保护用于冻结原模型的协同推理。训练额外小模块不等于微调原 LLM，故与 SGT 按同一标准归入 Inference。 |
| [SGT](../2_Embedding/Inference/Learning_Obfuscations_of_LLM_Embedding_Sequences_Stained_Glass_Transform.pdf) | `2_Embedding/Inference` | 目标 LLM M 冻结；只训练独立的 SGT 模型。 | §3–5，PDF 第 3–6 页；第 3 页图 2、第 5 页明确只更新 SGT weights。 | 有离线训练，但原模型完全不改，符合用户明确指定的 Inference 示例。 |
| [OSNIP](../2_Embedding/Inference/OSNIP_Balancing_the_Privacy-Utility-Efficiency_Trilemma_in_LLM_Inference_via_Obfuscated_Semantic_Null_Space.pdf) | `2_Embedding/Inference` | 冻结服务器预测模型 θ，只更新客户端混淆器 ϕ；训练时梯度经过冻结模型。 | §3.2–3.3，PDF 第 4–5 页；第 5 页明确 freeze θ and update ϕ。 | 独立学习保护映射，原 LLM 不微调，归入 Inference。文中“加密/语义零空间”是其方法命名，不等同于标准密码学安全保证。 |
| [VLM 图文上传保护](../1_Prompt/Privacy-preserving_for_user-uploaded_images_and_text_in_Vision-Language_Models.pdf) | `1_Prompt`；`5_Others` | 保护阶段使用公开代理模型；实验微调云端最后一个视觉层和最后一个 LLM 层，其余冻结。 | §4.1–4.3 与 §5.2，PDF 第 4–6 页；第 5 页最终 nearest-neighbor replacement token，第 6 页明确 Training setup。 | 最终上传的是处理后的图像和替换文本，属于 Prompt 与多模态数据保护（Others）。嵌入用于选替换词，并非上传受保护隐藏表示，因此不归入 Embedding/Inference；也不只因需要微调就误放 Embedding/Training。 |
| [SnD](../2_Embedding/Inference/Split-and-Denoise_Protect_Large_Language_Model_Inference_with_Local_Differential_Privacy.pdf) | `2_Embedding/Inference` | 原 LLM 参数不修改；额外训练本地去噪模型。 | §3–4，PDF 第 3–5 页；第 1 页摘要明确 no modifications to the model parameters。 | 冻结原模型的嵌入服务推理保护，是用户明确指定的 Inference 示例；不将其直接概括成完整聊天生成保护。 |
| [PIDI / ADMI](../4_Attack/From_Prompts_to_Responses_Dual-Sided_Data_Leakage_and_Defense_in_Split_Large_Language_Models.pdf) | `4_Attack`；`2_Embedding/Training` | 本地预热更新原头尾；随后整体训练，引入 VIB 和尾部正则，不是只外挂一个推理变换。 | §4–5，PDF 第 3–6 页；第 4 页 PIDI 图 2、第 5 页 ADMI 图 3 与第 6 页 Full Training。 | 同时提出新攻击与训练式防御，实体 PDF 交叉放入 Attack 与 Training。 |
| [RASR](../4_Attack/Inverting_the_Hidden_Unveiling_Multimodal_Privacy_Leakage_in_Collaborative_LVLM_Inference.pdf) | `4_Attack` | 训练和优化的是攻击侧重建模块；没有提出对应的训练式隐私防御。 | §IV–V，PDF 第 3–6 页；第 5 页图 2 展示对称重建与一致性细化。 | 研究贡献是隐私重建攻击；不能因为攻击器需要训练而归入 Embedding/Training。 |
| [Split LLM 微调综述](../5_Others/A_Survey_on_Split_Learning_for_LLM_Fine-Tuning_Models_Systems_and_Privacy_Optimizations.pdf) | `5_Others` | 综述，不适用单一冻结或微调设置。 | 摘要、§1–2，PDF 第 1–7 页；第 4 页图 1 为综述框架。 | 综合综述放入 Others，不把其中引用的攻击和防御全部算成该论文自身的方法。 |
| [FedAdOb](../5_Others/FedAdOb_Privacy-Preserving_Federated_Deep_Learning_with_Adaptive_Obfuscation.pdf) | `5_Others` | 共同训练自适应混淆模块与联邦模型；实验主体是通用深度网络而非 LLM。 | §3–4，PDF 第 3–5 页；第 5 页图 2 为 HFL/VFL 两种流程，实验见第 6–10 页。 | 作为通用联邦学习混淆的相关工作放入 Others，避免将普通视觉/表格联邦训练误标成 LLM 嵌入微调。 |
| [FL 隐私与 GDPR 综述](../5_Others/Privacy_Preservation_in_Federated_Learning_An_Insightful_Survey_from_the_GDPR_Perspective.pdf) | `5_Others` | 通用联邦学习综述，不适用单一 LLM 训练设置。 | 摘要、§4–5，PDF 第 1、9–18 页；第 11 页图 5 展示中央式 FL 的隐私与安全。 | 非 LLM 专用机制，且贡献是综述，归入 Others；摘要不作为现行法律意见。 |
| [PRIVEMB](../2_Embedding/Inference/Private_Release_of_Text_Embedding_Vectors.pdf) | `2_Embedding/Inference`；`5_Others` | 对现有文本向量做投影和随机化；不训练或微调原嵌入模型。 | §3–4，PDF 第 4–6 页；第 5 页算法 1 为 PRIVEMB。 | 机制上符合 Inference 的向量发布保护，同时是早期通用文本嵌入基础工作，并非完整自回归 LLM 推理协议，因此交叉放入 Others。 |

## 容易误分的情况

- **PrivPair**：原 PDF 文件名是 `Privacy-Preserving_Split_Learning_for_Federated_LLM_Fine-Tuning.pdf`，方法名在正文中。中间模型冻结，但原客户端首尾模型仍训练。
- **Privacy Adapters**：标题含 Prompt Inversion，保护接口实际是激活而非文本替换；原 Transformer 冻结，所以归 Embedding/Inference，不归 Prompt 或 Attack。
- **FedSEA-LLaMA**：前向状态加噪并用于后续推理，不等于整套方法无需微调。正文采用分割 LoRA 训练。
- **VLM 图文上传保护**：§4.3 在嵌入中加噪后检索为替换 token，上传对象仍是图文；§5.2 明确微调最后的视觉层与 LLM 层。原先的 Inference 目录不能直接沿用。
- **SplitLoRA / U-SplitDoRA**：收录为训练框架，不能将“数据/标签留本地”直接当作抵抗激活、梯度反演的证明。SplitLoRA 的 vanilla 流程还会发送标签，不能套用 U 形首尾留端的描述。
- **RASR**：训练攻击器是在增强攻击，不是训练式隐私保护。
- **TWIST / AloePri**：token 置换与模型权重变换是同一配套机制，不再拆出一份作为独立 Prompt 方法。两篇 PDF 分别保留，不因技术渊源相近合并。
- **综述**：只归 Others，不按其中综述了哪些方法做全目录重复。

## 原文核对与文件完整性

本地 DualGuard 的文本层用 pypdf 几乎只能抽取页码，已改用 PDFium 读取，并对照 [ACL Anthology 官方页面与原文](https://aclanthology.org/2025.acl-long.835/) 核实 §3。其余分类直接依据本地 PDF，不以旧目录名或旧研究笔记替代原文。

重排时保留每个 PDF 的原文件名和二进制内容；跨目录使用实体副本。重排后按 SHA-256 核对：20 个输入文件均存在，24 个目标副本逐一与原文件一致。`research_notes` 中原有研究方案与评审文档保留。
