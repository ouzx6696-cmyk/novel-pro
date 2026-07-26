---
pack_contract: 1
volume: {N}
genre_id: {题材编号}
parent_genre: {父题材或空}
formed_by: prompt.create 首任务（vol-N-act-K）
sources: [genre/<id>.md, genre/<parent>.md, webnovel/fanqie-baseline.md,
          plot/{实际选用的文件, 含 act-decomposition.md}, scene/{实际选用的文件, 含 self-contained-prompt.md}, character/{实际选用的文件}]
style_pointer: settings/writing-style.md
---

## 1. 读者与节奏基线
{连载基线 × 题材期待的合并压缩：本章最低交付、钩点节奏、空章/毒点禁忌，
 只留会改变章级决策的条目，不抄来源名}

## 2. 题材执行要点
{本题材的世界逻辑、成立条件、典型失败模式、表达要求的项目化压缩；
 与 settings/genre-setting.md 的作者确认内容对齐，不重复抄写，冲突以 genre-setting 为准}

## 3. 冲突、钩点与节奏方法
{plot 知识压缩：本卷幕结构下真正用得到的冲突成立条件、钩点布置、强弱交替、伏笔纪律}

## 4. 场景写法工具箱
{scene 知识压缩：按本卷高频场景类型（对白/对抗/调查/战斗/群像等）裁剪后的方法要点；
 低频类型不留全文，只留一行"出现时补读 scene/<file>.md"；
 必须包含自包含提示词方法 `scene/self-contained-prompt.md` 的核心压缩：
 三自原则摘要、各字段嵌入规则要点、自检五步法}

## 5. 人物决策与对手压力
{character 知识压缩：决策发动机、反派自洽压力、跨幕弧线连续的最小要点}

## 6. 文风提取接口
{指向 writing-style.md 的固定小节清单（声线定位/节奏配比/声线禁区/基准样章）
 +「本章质感」提取规则：每章取少量声线特征、一个节奏型、相关禁区、一句样句锚点}

## 7. 禁用与边界
{题材禁忌 + 作者边界（引自 genre-setting）+ 声线禁区指针；不新增规则，只做汇集}

## 8. 使用纪律
- 每章 Prompt 只取本章所需，不把包整段搬进 Prompt
- 不把方法名、来源名、术语写进 Prompt 或正文产物
- 包未覆盖的场景类型：允许单点补读一个知识文件，并在返回中说明，由顶层决定是否补入包
- 上游事实缺口或冲突：返回顶层，不自行补写
