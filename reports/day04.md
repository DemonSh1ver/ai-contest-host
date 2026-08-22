# 第 4 天实践报告：工程起步与环境复现

## 1. 基本信息

| 栏目 | 内容 |
| --- | --- |
| 课题 | 算法竞赛 AI 智能主持人 |
| 成员 | 姚子秋（独立完成，1 人） |
| 日期 | 2026-08-22 |

## 2. 今日目标

今天聚焦"工程能被别人复现"，不实现真实滚榜算法：

- 完善 README 启动说明
- 固定虚拟环境与依赖安装方式
- 验证项目可在独立环境首跑
- 梳理目录与脚本职责
- 通读现有代码并形成审查纪要
- 检查 `.gitignore`
- 完成至少一次真实 Git 提交
- 为 Day 5 的真实滚榜增强做好工程准备

## 3. 如何启动

### 环境要求

- Windows（TTS 走系统 SAPI5 语音引擎）
- Python 3.9+（本次验证环境为 3.13）
- 系统需安装中文 TTS 语音（Windows 自带 Microsoft Huihui Desktop - Chinese）

### 创建并激活虚拟环境

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动

```bash
python main.py            # 普通模式，从第 1 名播报到第 N 名
python main.py --roll     # 滚榜模式，从最后一名倒序逐队揭晓
python main.py <json文件> [--roll]   # 自定义榜单
```

### 停止方式

程序播报完整场后自动退出；中途停止按 `Ctrl+C`。

### 环境变量

当前版本不需要配置 API Key 或任何环境变量。

### 首跑验证标准

启动成功后应看到：控制台打印完整中文主持词（开场 → 逐队揭晓 → 结果 → 颁奖 → 结束），并出现 `[TTS] 已选用中文语音`，扬声器朗读中文。若出现 `[TTS] 警告：未检测到中文语音`，需在 Windows 设置中安装中文语音包。

## 4. 目录或工程结构

```text
ai-contest-host/
├── README.md              # 项目说明与启动说明
├── main.py                # 入口，串联四层并提供命令行参数与错误处理
├── requirements.txt       # 依赖（pyttsx3==2.99）
├── .gitignore             # 忽略虚拟环境、密钥、IDE 临时文件
├── test_invalid.json      # 失败用例输入（teams 类型错误）
├── src/
│   ├── parser.py          # 排行榜 JSON 解析
│   ├── roll.py            # 滚榜揭晓顺序（MVP 版，按 rank 倒序）
│   ├── script.py          # 主持词生成（普通 / 滚榜模式）
│   └── tts.py             # 语音合成与播放
├── data/
│   └── sample_leaderboard.json  # 样例排行榜
├── reports/               # 每日实践报告与失败记录
└── tests/                 # 单元测试
    ├── test_script.py     # 主持词生成测试
    └── test_parser_errors.py  # parser 异常输入测试
```

目录结构与 Day 2 架构一致，未新增 `event.py`、`Submission` 等后续增强模块。

## 5. 审查纪要

审查人：姚子秋；时间：2026-08-22；范围：当前 `main` 分支（commit `5f88cf7` 前的工作区）。

**问题 1**
- 文件：`main.py`
- 问题：非法输入（文件不存在、JSON 非法、`teams` 类型错误）直接输出完整 traceback，普通用户无法理解。
- 影响：演示或他人使用时遇错误输入会暴露底层堆栈。
- 处理：新增 `try/except` 捕获 `FileNotFoundError`、`json.JSONDecodeError`、`ValueError`，输出友好中文提示并返回退出码 1。
- 状态：已修复。

**问题 2**
- 文件：`README.md`
- 问题：仅含"安装依赖 + 3 条启动命令"，缺环境要求、虚拟环境、停止方式、环境变量、首跑验证标准。
- 影响：第二人无法按 README 独立跑通，不满足 Day 4 验收标准。
- 处理：补全上述各节。
- 状态：已修复。

**问题 3**
- 文件：`.gitignore`
- 问题：缺少 `.env`、`.idea/` 等本机环境与密钥忽略规则。
- 影响：可能误提交密钥或 IDE 临时文件。
- 处理：补 `.env`、`.env.*`、`*.key`、`*.pem`、`.idea/`。
- 状态：已修复。

**问题 4**
- 文件：`README.md`、`reports/day03.md`
- 问题：两者均写"第 4 天起实现真实滚榜"，与 Day 4 实际做工程起步矛盾。
- 影响：前后逻辑不一致。
- 处理：统一改为"第 5 天起"。
- 状态：已修复。

**复查无需修改项**：`script.py` 开场词已是赛后滚榜场景；`roll.py` 按 `rank` 倒序、无重复、不破坏排名；`tts.py` 含中文音色检测与语速音量配置；`parser.py` 异常处理齐全。

## 6. 协作与提交

- 团队方式：独立完成，仅使用 `main` 分支，无 feature 分支协作。
- 今日工程改动提交：commit `5f88cf7`，message `feat(day04): improve project startup and engineering setup`（含 README、`.gitignore`、`main.py`、`reports/day03.md`）。
- 本报告 `reports/day04.md` 将作为独立提交。

## 7. 今日完成与自检

**今日完成**：完善 README 启动说明；补全 `.gitignore`；修复 `main.py` 异常处理；完成独立 venv 首跑验证；形成审查纪要；完成一次真实 Git 提交。

**自检**：

| 检查项 | 结果 |
| --- | --- |
| 第二人能否按 README 独立启动 | 是（已在全新 `.venv` 复现跑通） |
| 安装命令是否正确 | 是（`pip install -r requirements.txt` 成功） |
| 启动/停止方式是否明确 | 是 |
| venv 是否可创建、依赖是否可装 | 是 |
| TTS 是否检测到中文语音 | 是（Microsoft Huihui Desktop - Chinese） |
| 目录结构是否清晰、`.gitignore` 是否完整 | 是 |
| 当前 MVP 是否仍可运行 | 是（19 个测试通过，`main.py --roll` 正常） |
| 审查纪要是否有真实问题与处理结果 | 是（4 个问题，均已修复） |
| 是否有不该提交的文件 | 无 |

## 8. 问题、计划与 AI 沟通

### 不成功的沟通

- 让助手直接生成 Day 4 报告时，助手一度默认把项目当成完整 Web/AI 系统，并抢跑 Day 5 的真实滚榜增强。处理方式：明确"Day 4 只做工程起步，真实滚榜第 5 天才开始"，并给出 8 章节固定结构后，输出才聚焦。
- 助手早期生成的启动命令与实际参数不一致（多写了不存在的参数）。处理方式：要求"先读当前 `main.py` 再写 README，不写不存在的参数"。

### 比较有效的沟通

- 要求助手"先检查当前代码，再决定是否修改，以实际运行结果为准，不默认完成"，据此发现并修复了 `main.py` traceback 问题。
- 要求 README 以"第二个人可以照着跑"为验收标准，据此补全了环境要求、虚拟环境、停止方式与首跑验证标准。
- 要求审查纪要写"文件 / 问题 / 影响 / 处理 / 状态"的真实问题，而非一句"已审查，没问题"。

### 明日安排

第 5 天开始进入真实滚榜增强：

1. 完善 `Submission` 样例数据；
2. 在 `roll.py` 实现简化 ICPC 风格题数与罚时计算；
3. 实现封榜后的隐藏提交解冻；
4. 每次解冻后重算成绩与排名；
5. 扩展 `RollStep` 记录旧/新排名与成绩变化；
6. 至少 3 支队伍构造发生一次排名变化的样例；
7. 保留 `python main.py --roll` 的现有 MVP 路径；
8. 为新增真实滚榜逻辑增加最小单元测试。
