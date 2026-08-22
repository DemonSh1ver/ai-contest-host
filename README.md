# AI Contest Host（算法竞赛 AI 智能主持人）

## 项目简介

本项目是一个「算法竞赛 AI 智能主持人」，面向算法竞赛赛后"滚榜播报"环节，自动完成"读榜 → 生成主持词 → 语音播报"全流程，替代人工逐队念榜，营造竞赛滚榜的紧张感与氛围感。

## 课题与使用场景

**课题及选用理由：** 针对算法竞赛赛后"滚榜播报"环节中人工念榜耗时、易错、节奏不一的痛点，用程序自动完成全流程播报。

**主要使用者 / 使用场景：** 算法竞赛赛事组织者与主持人，在比赛结束后将排行榜 JSON 导入程序，一键启动即可自动滚榜播报。

**课内交付边界：** 以"标准台式机 + 系统自带中文 TTS 语音引擎（离线）"为交付边界，仅交付命令行程序，不依赖联网 API、GPU 算力或外部音频设备。

## 项目目标

完整处理流程：排行榜 JSON → 数据解析 → 生成主持词 → TTS 语音 → 播放。

## 项目周期

2026-08-19 至 2026-08-27（共 9 天）。

## 方案组成

按第 2 天确定的技术选型，把链路拆成 4 个模块 + 1 个入口，模块间为单向数据流（`parser` 产榜单 → `roll` 产揭晓顺序 → `script` 产中文文本 → `tts` 播放）：

| 模块 | 职责 |
| --- | --- |
| `src/parser.py` | 读取排行榜 JSON，解析为队伍列表（标准库 `json`） |
| `src/roll.py` | 给出「从最后一名到第一名」的滚榜揭晓顺序 |
| `src/script.py` | 按滚榜顺序生成中文主持词（普通 / 滚榜模式） |
| `src/tts.py` | 把主持词文本转为中文语音并播放（`pyttsx3`，离线） |
| `main.py` | 串联上述四层，提供命令行入口 |

## 项目基础结构

```text
ai-contest-host/
├── README.md                        # 项目说明与启动说明
├── main.py                          # 程序入口
├── requirements.txt                 # 依赖（pyttsx3）
├── .gitignore                       # 忽略虚拟环境、密钥、IDE 临时文件等
├── test_invalid.json                # 失败用例输入（teams 类型错误）
├── src/
│   ├── parser.py                    # 榜单解析
│   ├── roll.py                      # 滚榜揭晓顺序
│   ├── script.py                    # 主持词生成
│   └── tts.py                       # 语音合成播放
├── data/
│   └── sample_leaderboard.json      # 样例排行榜
├── reports/                         # 每日实践报告与失败记录
│   ├── day01.md / day02.md / day03.md
│   └── day03_failure_example.txt / day03_parser_failure_log.txt
└── tests/                           # 单元测试
    ├── test_script.py               # 主持词生成测试
    └── test_parser_errors.py        # parser 异常输入测试
```

## 使用方法

### 环境要求

- Windows（TTS 走系统 SAPI5 语音引擎）
- Python 3.9+（当前开发环境为 3.13）
- 系统需安装中文 TTS 语音（Windows 自带 Microsoft Huihui Desktop - Chinese 即可）

### 创建虚拟环境

```bash
python -m venv .venv
```

### 激活环境（Windows）

```bash
.venv\Scripts\activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动

播放默认样例（普通模式，从第 1 名到第 N 名播报）：

```bash
python main.py
```

滚榜模式（从最后一名倒序逐队揭晓）：

```bash
python main.py --roll
```

播放自定义排行榜：

```bash
python main.py path/to/leaderboard.json
python main.py path/to/leaderboard.json --roll
```

### 停止方式

程序播报完整场后自动退出；若需中途停止，按 `Ctrl+C`。

### 环境变量

当前版本不需要配置 API Key 或任何环境变量。

### 首跑验证标准

启动成功后应看到：

1. 控制台打印完整中文主持词（开场 → 逐队揭晓 → 结果 → 颁奖 → 结束）；
2. 出现 `[TTS] 已选用中文语音`，且扬声器朗读中文播报。

若出现 `[TTS] 警告：未检测到中文语音`，说明系统缺少中文语音包，需在 Windows 设置中安装中文语音后重试。

## 当前开发阶段

已完成第 1~3 天工作：

- 第 1 天：确认选题与 MVP 边界（单机命令行，不做计分 / 排名计算）。
- 第 2 天：确定方案组成与技术选型（`json` + `pyttsx3` + `unittest`）。
- 第 3 天：固定主路径数据对象（`Team` / `Leaderboard` / `RollStep` / 主持词文本）与调用约定（含成功、失败案例），跑通 `解析 → 滚榜 → 主持词 → TTS 播放` 完整链路，`python main.py` 可实际出声。

当前滚榜为 MVP 版：按输入榜单的名次（`rank`）倒序揭晓，不重新计算得分与排名。真实滚榜（`Submission` 数据、简化 ICPC 罚时、封榜解冻、排名变化）与事件识别均属于 MVP 之外的特色增强，计划第 5 天起在不破坏 MVP 的前提下逐步实现。
