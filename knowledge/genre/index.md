# 题材索引

读取项目 `settings/genre-setting.md` 的 `genre_id`，再读取对应文件。细分题材文件
会声明父题材；使用时先查下方"主题材速写"获取父级上下文，只有需要完整细节
（典型失败模式、表达要求等）时才读父题材文件。题材知识只改变读者期待、节奏、
世界逻辑和表达选择，不替作者决定剧情。

## 题材注册表

| genre_id | 中文名 | parent |
|---|---|---|
| `xianxia` | 东方仙侠 | - |
| `xuanhuan` | 东方玄幻 | - |
| `xuanhuan-brained` | 玄幻脑洞 | `xuanhuan` |
| `urban` | 都市 | - |
| `urban-daily` | 都市日常 | `urban` |
| `urban-romance` | 都市甜宠 | `urban` |
| `urban-farming` | 都市种田 | `urban` |
| `urban-brained` | 都市脑洞 | `urban` |
| `urban-cultivation` | 都市修真 | `urban-brained` |
| `urban-high-martial` | 都市高武 | `urban-brained` |
| `suspense-crime` | 悬疑犯罪 | - |
| `suspense-paranormal` | 悬疑灵异 | `suspense-crime` |
| `suspense-brained` | 悬疑脑洞 | `suspense-crime` |
| `historical` | 历史 | - |
| `historical-brained` | 历史脑洞 | `historical` |
| `ancient-politics` | 古代权谋 | `historical` |
| `anti-japanese-war` | 抗战谍战 | `historical` |
| `scifi-apocalypse` | 科幻末世 | - |
| `western-fantasy` | 西方奇幻 | - |
| `war-god` | 战神归来 | `urban` |
| `derivative` | 同人衍生 | - |
| `anime-derivative` | 动漫衍生 | `derivative` |
| `male-derivative` | 男频衍生 | `derivative` |
| `game-sports` | 游戏体育 | - |

## 主题材速写

读子题材时，先从这里获取父级上下文；需要完整细节（失败模式、表达禁忌等）再读父文件。

- **xianxia（东方仙侠）**：修行体系与境界压制可信；道心/因果/天劫让选择有代价；期待超脱与人间牵绊的张力。
- **xuanhuan（东方玄幻）**：清晰成长反馈、势力冲突、更大世界逐步展开；战力等级压制可感，越级要有条件；能力效果、代价与克制稳定。
- **urban（都市）**：熟悉社会环境中的身份、资源、关系和现实后果；职业流程、收入消费、城市常识可信；口语生活化，场景落到可感知生活细节。
- **suspense-crime（悬疑犯罪）**：线索公平、推理可回看、调查有现实阻力；证据链、程序、认知边界可信；巧合不能承担核心破案。
- **historical（历史）**：时代洪流中的具体选择；制度、礼法、资源限制让行动有重量；人物行为符合时代认知，阶层身份约束行动空间。
- **scifi-apocalypse（科幻末世）**：生存资源真实稀缺、技术有代价有边界；秩序崩塌后人际博弈有生存逻辑；科学设定自洽不为反转临时改口。
- **western-fantasy（西方奇幻）**：魔法有规则有代价；种族/文化差异影响行为逻辑；旅途受补给地形影响，胜利改变关系和格局。
- **derivative（同人衍生）**：角色声音还原、改动追踪后果、独立因果成立；读者期待"如果……会怎样"的推演，不是百科重述。
- **game-sports（游戏体育）**：胜负有训练和策略支撑、对手有独立意志；赛制/规则持续约束；成长可量化但不靠临场爆种。

未注册题材：选择最接近的主类型作为临时参考，并由作者确认真正的读者期待和
禁忌；不要伪装成已有精确规则。

题材画像只给期待、约束和差异，不给固定章型或情节案例。planner 必须从当前人物、
卷目标和资源关系推导事件，不能把题材文件当桥段库。

连载向项目默认叠加 `knowledge/webnovel/fanqie-baseline.md`（与具体 genre_id
正交，不是新的题材编号）。题材画像只改读者期待、节奏、世界逻辑与表达选择，
不替作者决定剧情，不做字段门禁。

## 与 anti-ai/genre/ 的关系

`knowledge/genre/` 下的题材文件服务规划阶段（planner、prompt-crafter），提供读者期待、
节奏、世界逻辑和失败模式。`knowledge/anti-ai/genre/` 下的题材文件服务表达编辑阶段
（anti-AI editor），提供优先删改、优先保留和处理口径。两者同名但内容不同、
消费者不同，不是重复。修改某一侧的题材认知时，检查另一侧是否需要同步调整。
