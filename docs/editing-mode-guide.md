# 编辑模式专项指南

编辑模式是 novel-pro 的核心质量保障机制。本文档解释为什么需要六步流程、每步做什么、典型场景演示和常见问题。

---

## 目录

1. [为什么需要六步流程](#为什么需要六步流程)
2. [六步流程详解](#六步流程详解)
3. [典型场景演示](#典型场景演示)
4. [常见问题FAQ](#常见问题faq)

---

## 为什么需要六步流程

### 设计理念

编辑模式的核心目标：**把草稿编辑到作者可接受、可发布的完成度**。

这不是简单的"改错别字"，而是经过完整的文学验收流程：

1. **Writer写首稿** - 把Prompt写成人物的行动过程
2. **Reader冷读** - 以读者身份发现内容问题
3. **Anti-AI扫描** - 以规则发现表达问题
4. **整体裁决** - 综合两份报告，分级返修
5. **分流返修** - 按问题类型选择返修路径
6. **复读提交** - 验证返修效果，写入正文

### 为什么不简化？

每一步解决不同层面的问题：

```
Writer  解决: Prompt是否被正确执行
Reader  解决: 内容是否有文学价值
Anti-AI 解决: 表达是否有AI味
Synth   解决: 返修优先级和路径
Repair  解决: 具体问题
Commit  解决: 最终验收和提交
```

跳过任何一步都会留下对应层面的问题。

### 为什么需要双报告？

**Reader冷读**和**Anti-AI扫描**解决不同问题：

| 维度 | Reader冷读 | Anti-AI扫描 |
|---|---|---|
| 发现什么 | 内容问题（因果/人物/场景/承接） | 表达问题（AI味/模板化/解释腔） |
| 怎么发现 | 以读者身份阅读，产生真实反应 | 按规则扫描，识别表达模式 |
| 能发现对方不能发现的 | 人物动机不成立、场景骨架倒塌 | 微妙的AI味、机械重复 |
| 不能发现的 | 表达层面的细微问题 | 内容是否成立（只看表达） |

两份报告互补，edit-synthesizer综合裁决。

---

## 六步流程详解

### 第1步：edit.write - Writer写首稿

**做什么**：为每章构造writer base，创建独立writer，交付Prompt。

**输入**：
- 单章writer base（顶层构造）
- 单章Prompt

**输出**：
- `drafts/vol-N-ch-M.md`（草稿）

**关键点**：
- 每章独立writer，独立上下文
- Writer不读知识库、设定、规划
- 完全依赖base+Prompt

**完成判定**：所有目标章节草稿形成

**下一步**：edit.review

---

### 第2步：edit.review - Reader冷读

**做什么**：Reader单章冷读正文（阅读上下文含本章之前全部已提交正文），产出冷读报告。

**输入**：
- 本章正文和候选（+ 本章之前的已提交正文作为上下文）

**冷读纪律**：
- 首读不读规划、Prompt、知识、报告
- 先产生真实阅读反应
- 首读后才追查根因

**输出**：冷读报告
```markdown
verdict: PASS / FIX / STOP
chapter: vol-1-ch-2

## 已成立处
{哪些人物、动作、关系已经成立}

## 首读
{真实阅读反应}

## 问题与处理
- {章节}: {正文证据} -> {读者影响} -> {根因} -> {建议角色} -> {最小处理}

## 不应改变
{返修时必须保留的内容}

## 仍未解决
{本轮未闭合的问题}

## 最终复读
{PASS / FIX / STOP 与仍保留的事实}

## 接受候选
- {章节}: {task 候选路径}
```

**关键点**：
- 先记成立处，再记问题
- 没有正文证据的问题不进入返修
- HARD FIX: synopsis delivery（关键场景只剩概述）

**完成判定**：报告给出verdict与复读范围

**下一步**：edit.anti-ai

---

### 第3步：edit.anti-ai - Anti-AI全量扫描

**做什么**：Anti-AI对本章正文全量扫描表达问题（顺序链路逐章闭环）。

**输入**：
- Reader读过的本章正文
- `knowledge/anti-ai/index.md`（通用+题材规则）

**不依赖**：不依赖Reader点名，主动全量扫描

**输出**：Anti-AI报告
```markdown
chapter: vol-1-ch-2
scanned: 全量

### ch-2
- 等级: 严重 / 中等 / 轻微
- 证据: {原句定位} -> {AI味表现}
- 边界: 局部可编辑 / 越界
- 处理倾向: anti-ai编辑 / 升级
```

**关键点**：
- 只列证据，不动文
- 标注是否越出局部编辑边界
- 不依赖Reader的报告

**完成判定**：本章经全量扫描

**下一步**：edit.synthesize

---

### 第4步：edit.synthesize - 整体返修裁决

**做什么**：edit-synthesizer综合两份报告，分级并给整体返修意见。

**输入**：
- Reader冷读报告
- Anti-AI报告
- （分歧时）最小正文核对

**输出**：整体返修意见
```markdown
act: vol-1-act-2

### 严重（优先处理）
- ch-M: {来源} {问题} -> REGENERATE -> {writer/prompt-crafter/planner}

### 中等
- ch-Q: {来源} {问题} -> 改写局部

### 轻微
- ch-R: {来源: anti-ai} {问题} -> anti-ai编辑模式

### 跨章关联
{哪些章的问题相互牵连}

### 优先级与执行顺序
{返修顺序}
```

**分级标准**：
- **严重**：核心因果/人物动机/信息时序/场景骨架失败 -> REGENERATE
- **中等**：明显阻碍阅读的理解偏差/结构松散 -> 改写局部
- **轻微**：局部措辞/机械重复/解释腔 -> anti-ai编辑

**分流建议**：
- REGENERATE -> writer（原Prompt）/ prompt-crafter（修Prompt）/ planner（调规划）
- 局部表达 -> anti-ai编辑模式
- 正文成立 -> IGNORE

**完成判定**：所有问题均被分级、归属并给出返修意图

**下一步**：edit.repair 或 edit.commit（无返修项时直接提交）

---

### 第5步：edit.repair - 分流返修

**做什么**：按整体返修意见执行返修。

**分流路径**：

#### REGENERATE（严重问题）
1. **正文执行不足** -> 新writer（原Prompt）重写完整章节
2. **Prompt不足** -> prompt-crafter修Prompt -> 新writer重写
3. **规划冲突** -> 对应planner调整 -> 修Prompt -> 重写

#### 局部表达（中等/轻微）
- anti-ai编辑模式，在edit-boundary内局部修改
- 不新增场景/线索/改变剧情/改变POV/改变声线/改变字数

**输入**：整体返修意见 + 受影响正文

**输出**：
- draft candidate（writer重写）
- 修复Prompt
- 重建规划
- 表达候选（anti-ai编辑）

**关键点**：
- 原draft和候选保留在task中供Reader复读比较
- 不作为内容writer的创作输入

**完成判定**：每个候选完成

**下一步**：Reader复读

---

### 第6步：edit.commit - 提交正文

**做什么**：Reader复读通过后，novel-agent预检并写入texts/。

**前置条件**：
- Reader已复读受影响范围
- 无未解决问题
- 无未解决HARD FIX
- 幕终点成立

**预检步骤**：
1. 只读取Reader报告中列出的接受候选
2. 确认全部候选是纯小说正文
3. 预检全部目标路径
4. 任一候选混入说明或不完整时停止
5. 目标存在且内容不同时停止

**写入**：`texts/vol-N-ch-M.md`

**提交后**：
- 清理当前task的返修候选和临时报告
- 删除已消费的draft
- 失败保留现场供order恢复

**幕间校准**：
- 比较texts/的实际终点与下一幕start_state
- 一致时直接推进
- 有偏差时只校准尚未执行的幕纲/章纲/Prompt
- 已接受正文不回写

**下一步**：下一幕 / volume.complete

---

## 典型场景演示

### 场景1：一切顺利

```
edit.write -> 3章草稿形成
edit.review -> Reader冷读，verdict: PASS
edit.anti-ai -> 扫描完成，无严重问题
edit.synthesize -> 无返修项
edit.commit -> 直接提交到texts/
```

**耗时**：约15-20分钟/幕

---

### 场景2：表达问题返修

```
edit.write -> 3章草稿形成
edit.review -> Reader冷读，内容成立
edit.anti-ai -> 发现ch-2有"解释腔"（中等），ch-3有"机械重复"（轻微）
edit.synthesize -> 分级：ch-2中等表达，ch-3轻微表达
edit.repair -> anti-ai编辑模式局部修改
Reader复读 -> 原问题解决，无新问题
edit.commit -> 提交到texts/
```

**耗时**：约25-30分钟/幕

---

### 场景3：内容问题返修

```
edit.write -> 3章草稿形成
edit.review -> Reader冷读，发现ch-2的HARD FIX（关键场景只剩概述）
edit.anti-ai -> 扫描完成
edit.synthesize -> ch-2归为严重，根因：正文执行不足
edit.repair -> 新writer用原Prompt重写ch-2
Reader复读 -> ch-2重写后场景展开充分
edit.commit -> 提交到texts/
```

**耗时**：约30-40分钟/幕

---

### 场景4：Prompt问题返修

```
edit.write -> 3章草稿形成
edit.review -> Reader冷读，发现ch-1和ch-3都有同类执行问题
edit.anti-ai -> 扫描完成
edit.synthesize -> ch-1和ch-3同类问题，根因：Prompt设计不足
edit.repair -> prompt-crafter修Prompt -> 新writer重写
Reader复读 -> 重写后问题解决
edit.commit -> 提交到texts/
```

**耗时**：约40-50分钟/幕

---

## 常见问题FAQ

### Q1: 为什么不能跳过Anti-AI扫描？

**A**: Anti-AI扫描能发现Reader可能忽略的微妙表达问题：
- 微妙的AI味（不明显但累计影响阅读体验）
- 机械重复（跨章的句式重复）
- 解释腔（直接告诉读者人物在想什么）

Reader关注内容是否成立，Anti-AI关注表达是否自然。两者互补。

### Q2: 为什么需要edit-synthesize综合裁决？

**A**: 因为：
1. **避免重复返修**：两份报告可能指向同一章的不同层面，综合裁决避免对同一章多次返修
2. **确定优先级**：严重问题先处理，轻微问题后处理
3. **跨章关联**：某些问题跨章牵连，需要一并处理
4. **分流决策**：内容问题走writer，表达问题走anti-ai，不能混在一个返修任务里

### Q3: 返修后为什么要重新顺序冷读？

**A**: 因为：
1. **返修可能引入新问题**：修改后的段落可能与上下文不连贯
2. **复读是新冷读**：不能只检查原问题是否消失，要重新判断整体阅读体验
3. **声线一致性**：返修段落可能与全章声线不一致

只检查原问题卡是最大的返修验证错误。

### Q4: 什么时候用REGENERATE，什么时候用局部编辑？

**A**: 判断标准：

| 问题类型 | 返修路径 |
|---|---|
| 核心因果失败 | REGENERATE（新writer） |
| 人物动机不成立 | REGENERATE |
| 信息时序错误 | REGENERATE |
| 场景骨架倒塌 | REGENERATE |
| 关键场景只剩概述（HARD FIX） | REGENERATE |
| 明显阻碍阅读的理解偏差 | 改写局部 |
| 结构松散 | 改写局部 |
| 较重的模板化表达 | 改写局部 |
| 局部措辞问题 | anti-ai编辑 |
| 机械重复 | anti-ai编辑 |
| 解释腔 | anti-ai编辑 |
| 不自然对白 | anti-ai编辑 |

**边界原则**：跨章事实或核心因果问题必须走REGENERATE，不能由局部编辑器处理。

### Q5: edit.commit的预检失败怎么办？

**A**: 预检失败时不写任何目标，保留现场。可能原因：
1. 候选混入说明文字 -> 返修writer
2. 正文不完整 -> 返修writer
3. 目标已存在且内容不同 -> 人工确认后处理

**原则**：不在写入前停止，不覆盖任何目标。

### Q6: 编辑模式和完本质检有什么区别？

**A**:

| 维度 | 编辑模式 | 完本质检 |
|---|---|---|
| 触发 | 创作流程中 | 作者显式要求 |
| 范围 | 一幕 | 全书 |
| 目标 | 逐幕验收并提交 | 全书冷读，发现遗漏 |
| 角色 | reader + anti-ai + synthesize | completion-reviewer |
| 分流 | FIX/STOP | IGNORE/EDIT/REGENERATE |
| 改变cursor | 是（review -> volume.complete） | 否（旁路） |

完本质检是编辑模式的补充：即使每幕都过了编辑模式，全书冷读可能发现跨幕问题。

### Q7: 可以只用写作模式不用编辑模式吗？

**A**: 可以。写作模式产出草稿到drafts/，不进入编辑模式流程。但：
- 草稿未经Reader验收
- 没有经过Anti-AI扫描
- 不能写入texts/

如果后续需要精修，可以从drafts/进入编辑模式。

### Q8: 幕间校准是什么？

**A**: 提交当前幕后，比较texts/的实际终点与下一幕start_state：
- **一致**：直接推进到下一幕
- **有偏差**：只校准尚未执行的幕纲/章纲/Prompt
- **已接受正文不回写**：不动已经提交的texts/

幕间校准确保规划与正文的一致性，但不破坏已接受正文。

---

## 相关文档

- [框架总览](framework-overview.md) - 整体架构和数据流
- [接口参考](interface-reference.md) - 操作契约和角色接口
- [模板填写指引](templates-guide.md) - 模板字段说明
- [示例文档](examples.md) - 报告格式示例
- [新手入门](getting-started.md) - 快速开始