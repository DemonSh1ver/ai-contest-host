# AI Contest Host（算法竞赛 AI 智能主持人）

## 项目简介

本项目是一个「算法竞赛 AI 智能主持人」，用于在算法竞赛场景中自动生成主持词并进行语音播报。

## 项目目标

完整处理流程：排行榜 JSON → 数据解析 → 生成主持词 → TTS 语音 → 播放。

## 模块划分

```text
ai-contest-host/
├── main.py                    # 程序入口：串联 解析 → 主持词 → 播报 全流程
├── requirements.txt           # 依赖：pyttsx3
├── src/
│   ├── __init__.py
│   ├── parser.py              # 排行榜 JSON 解析（标准库 json，支持字段容错）
│   ├── script.py              # 主持词生成（数字转中文 + 播报文案）
│   └── tts.py                 # 语音合成与播放（pyttsx3，离线）
├── data/
│   └── sample_leaderboard.json  # 样例排行榜（格式约定参考）
└── tests/
    └── test_parser.py         # 解析模块单元测试
```

## 使用方法

### 播放样例排行榜

```bash
python main.py
```

### 播放自定义排行榜

```bash
python main.py path/to/leaderboard.json
```

### 滚榜模式（ICPC/CCPC 颁奖名场面）

```bash
python main.py --roll
```

从最后一名开始逐队揭晓，每队拆成「名次悬念 + 揭晓」两段播报并停顿，台词随名次推进逐级拉高悬念。

### 运行单元测试

```bash
python -m unittest discover -s tests
```

## 当前开发阶段

- [x] 第 1 天：选题确认、Git 初始化、项目骨架
- [x] 第 2 天：TTS 引擎选型（pyttsx3）、JSON 解析方式（标准库 json）、模块划分
- [ ] 第 3 天：主持词生成脚本与样例数据
- [ ] 后续：语音调优、特殊队名读音映射等
