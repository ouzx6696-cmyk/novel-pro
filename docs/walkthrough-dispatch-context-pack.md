# 派发整合与 Context Pack 实施走查

日期：2026-07-26 ｜ 基于方案 `docs/plan-dispatch-and-context-pack.md` ｜ 版本 `0.2.2-pro`

本走查按方案第八节清单对四阶段实施结果做静态 + 实测验证。

## 一、阶段一 · 派发矩阵

- [x] `skills/dispatch.md` 所有权大表重构为 **15 张 operation 派发卡**（`^- 触发：` 计数 = 15），与 cursor 表、order.operation 表一一对应、无新增 operation。
- [x] `agents/novel-agent.md` 删除「项目启动 / Prompt 创建 / 创建 Writer / Fast / Full」五节流程散文，收敛为「派发指针 + 创建 Writer 指针」，保留控制面所有权、版本门禁、状态与恢复（68 行 → 约 40 行）。
- [x] `SKILL.md` 路由节从主题索引改为 **15 行 operation → 模块 → 角色**索引表；`prompt.create` 行含 `+ skills/context-pack.md` 引用；Fast/Full 两节删除流程图，改为指向 dispatch.md「创作循环」的指针。
- [x] `skills/writing.md` 开头加「调度时序以 dispatch.md 派发卡为准」声明；删除 Fast/Full 两节重复流程图，保留 writer 构造与正文阅读判断细节。
- [x] 全局检索 Fast/Full 流程图箭头（`fast.write`：每章构造 writer base）**仅存在于 `dispatch.md`「创作循环」一处**，其余位置均为指针。

## 二、阶段二 · Context Pack 契约

- [x] 新增 `skills/context-pack.md`：建包 / 用包 / 补包 / 重建规则 + 与既有契约关系（Reader 冷读、writer 边界、anti-ai 隔离、迁移、alignment 全部明确保留）。
- [x] 新增 `templates/settings/context-pack.md`：8 节预制包模板（frontmatter 含 pack_contract / volume / genre_id / sources / style_pointer）。
- [x] `skills/prompt.md`「创作上下文」节：默认输入改为读 `settings/context-pack.md`，本卷首任务先按 `skills/context-pack.md` 建包。
- [x] `agents/prompt-crafter.md`：frontmatter 5 个知识挂载描述标注「本卷首任务建包时读取」；「所有权与输入」节输入首项为 context-pack、首任务另写 `settings/context-pack.md`。
- [x] `knowledge/index.md`：第 19 行追加 pack 合法性声明（读包即视为完成知识加载，不构成"跳过"）；webnovel 使用者行注明「首任务建包，后续读 pack」。
- [x] `skills/dispatch.md`：`项目事实的承接`表加 context-pack 一行；`prompt.create` 派发卡含「首任务建包、pack 未漂移不重建」；`恢复`节加 pack 声明。

## 三、阶段三 · 边缘同步

- [x] `skills/migration.md`：加「派生产物不搬运；新项目首任务重建 pack」说明。
- [x] `skills/volume-alignment.md`：加「预制包漂移核对」节。
- [x] `README.md`：Prompt 创建附近加一句 pack 简介。
- [x] `tools/runtime_manifest.py`：SKILL_FILES 加 `context-pack.md`（计数验证 = 1）。
- [x] `tools/init.py`：REQUIRED_SOURCE_FILES 加模板、deploy_project_files 加 copy_if_missing（计数验证 = 2）。

## 四、实测验证（阶段三 工具登记）

- [x] `python -m py_compile tools/init.py tools/runtime_manifest.py`：无语法错误。
- [x] `python tools/init.py <tmp> --genre-name urban` 成功；生成 `settings/context-pack.md` 且部署 `.claude/skill-resources/skills/context-pack.md`。

## 五、未执行的动态验证（需真实写作项目运行）

以下项静态已确保模板/模块齐备，待真实卷运行确认：

- [ ] 测试项目首任务建包：pack 落盘、sources 与实际读取一致、不含方法名/来源名直抄。
- [ ] 第二个 `prompt.create` 任务全程未打开 `knowledge/` 下文件（除 pack 声明的补读例外）。
- [ ] Prompt 产物结构与质量不变（`prompt_contract: 2` 全字段、「本章质感」仍从 `writing-style.md` 提取）。
- [ ] Reader 冷读路径未出现 pack；anti-ai 文件未进 pack。
- [ ] 迁移项目：`.migration/report.md` 不列 pack 为缺失；新项目首任务重建 pack。

## 六、边界遵守确认

- 未增加门禁 / 评分 / 关键词 / 字数脚本。
- 未新增角色（建包由 prompt-crafter 兼任）。
- 未改变 cursor / order.operation 集合（建包挂在首个 `prompt.create` 任务内）。
- Reader 冷读保护、writer 自包含边界、anti-ai 按需隔离均未改动。
- 版本门禁与迁移判定条件原样保留。
