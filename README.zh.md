# Strata

**一套测试驱动的 vibe coding 方法论。**

*得名于地质层理——层层叠加，共同讲述完整的故事。*

[English](README.md)

---

AI 写代码的速度已经超过了你审查的速度。这就是问题所在。

不是写的问题——是知道的问题。知道写出来的东西是否真的能跑。知道它有没有把别的东西搞坏。知道，有凭有据地知道，这个功能做完了，而不只是"做完了"。

Strata 是为这个现实设计的测试方法论和项目模板。三层测试。一套选层决策规则。还有 AI 编程助手 skill，把方法论编码进去，让你的 agent 做出和你最好的工程师一样的判断。

---

## 三层金字塔

```
              ╱╲
             ╱  ╲           browser
            ╱ B  ╲          把产品当黑盒 · 分钟级
           ╱──────╲
          ╱   U    ╲        unit
         ╱          ╲       纯逻辑 · 秒级
        ╱────────────╲
       ╱      S       ╲     static
      ╱                ╲    结构不变量 · 毫秒级
     ╱──────────────────╲
```

| 层 | 问题 | 速度 | 依赖 |
|----|------|------|------|
| `static` | 结构还撑得住吗？ | < 0.3s | 无 |
| `unit` | 逻辑是对的吗？ | < 5s | 无服务器 |
| `browser` | 产品能用吗？ | 分钟级 | 运行中的产品 |

**Static** — `pytest harness/static.py`，无服务器，无导入。用正则和 AST 检查源文件：禁用模式、必须存在的文件、handler 覆盖率。一个新路由绕过了 auth？服务器启动之前就在这里被抓到了。

**Unit** — `pytest harness/unit.py`，无服务器，外部调用 mock。纯函数、解析器、状态机。每个测试都有一个 docstring 回答：*如果这个 test 挂了，产品上会坏什么？* 没有这个答案的测试，挂了会被删掉而不是被修。

**Browser** — 产品运行在 Docker 里。Driver 打开真实浏览器，执行一个 scenario——一个描述用户流程、观察点和断言的 markdown 文件。文字证据提交进 `browser-tests/reports/`。没有 committed 证据的 scenario run，等同于没跑过。

---

## 选层决策树

```
  你在测什么？
         │
         ├── 结构事实、代码 pattern、文件存在性？  ──► static
         │
         ├── 纯函数、解析器、状态机？              ──► unit
         │
         └── API、UI、数据库、WebSocket、文件状态？ ──► browser

  多层都受影响？→ 每层都加，不省略。
```

---

## Scenario

Scenario 是一个 markdown 文件，它是内容，不是代码。可执行的测试代码会把测试绑定到特定的库和版本——markdown scenario 描述的是*用户做了什么、产品必须证明什么*，这个描述比任何 driver 都活得更长。

每个 scenario 包含以下部分：

```
 Fixtures ──► Actions ──► Wait/Settling ──► Sensors ──► Asserts ──► Report ──► Cleanup
```

| 部分 | 写什么 |
|------|--------|
| Purpose | 一句话：被测行为是什么 |
| User Flow | 从用户视角描述的操作步骤 |
| Fixtures | 所需的初始状态 |
| Actions | 与 driver 无关的操作："点击提交"，不是 `page.click('#submit')` |
| Wait/Settling | 命名的异步收敛点，含超时设置 |
| Observations | DOM、网络、server 日志、数据库状态、文件系统状态 |
| Asserts | 明确的 pass/fail："DOM 显示 `Welcome, Alice`"，不是"用户已登录" |
| Report | 必须提交的文件及路径 |
| Cleanup | 留下的或清理掉的状态 |

---

## Browser

Driver 在运行中的产品上执行 scenario。三种平级 driver——切换 driver 不需要重写 scenario：

| Driver | 模式 | 适合场景 |
|--------|------|----------|
| `playwright` | 脚本化 | CI、确定性自动化 |
| `browser-use` | AI 驱动 | 自然语言操作 |
| `claude-in-chrome` | 交互式 | 调试、可视化检查 |

一次 run 之后的证据路径：

```
browser-tests/
├── reports/                    ← 提交到 git
│   └── <scenario>/<run-id>/
│       ├── report.md
│       ├── report.json
│       ├── dom.txt
│       ├── network.json
│       └── server.log
└── artifacts/                  ← gitignored（仅二进制）
    └── <scenario>/<run-id>/
        └── screenshot.png
```

---

## 开发原则

| 原则 | 规则 |
|------|------|
| **奥卡姆剃刀** | 如非必要，不增加实体。 |
| **测试先行** | 先写失败的测试，再写实现。 |
| **全量验证** | 任何改动都跑所有受影响的测试。 |
| **不容忍 silent exception** | 每个异常必须被日志记录、重新抛出，或有明确理由。 |
| **降低复杂度** | 更少的代码、更少的概念、更少的移动部件。 |
| **横向思考** | 没有特殊情况——找到并列的实体。 |
| **错误先行** | 先设计失败路径，再实现 happy path。 |

---

## 设计选择

**Driver 可以互换。** Scenario 是 markdown 文件。Playwright、browser-use、Claude in Chrome 是同一套 contract 的平级实现。切换 driver 不需要重写 scenario。

**Evidence 分类是强约束。** 文字证据（DOM、日志、JSON）commit 进 `browser-tests/reports/`。二进制证据（截图、视频）放在 `browser-tests/artifacts/`，gitignore。repo 精简，可复现性完整。

**Tracking file 是契约。** 写代码之前，先写一个带测试计划的 tracking file。它从 `todo/` 移到 `done/` 的条件是：测试通过，证据存在。

**Skill 是可执行的方法论。** 三个 skill——`static`、`unit`、`browser`——不是文档，是指令。在 AI 助手内部运行。agent 调用 static skill，做出的选层判断和你最好的工程师一样。方法论随 repo 走。

---

## 核心概念

| 概念 | 含义 |
|------|------|
| 层（Layer） | `static`、`unit` 或 `browser`——每层回答不同问题 |
| Tracking file | 带测试计划的 markdown 文件，从 `todo/` 移到 `done/` |
| Scenario | 描述用户流程的 markdown 文件，与 driver 无关 |
| Driver | 执行 scenario 的工具：`playwright`、`browser-use`、`claude-in-chrome` |
| Evidence | 文字证据 commit 进 `browser-tests/reports/`；二进制本地 gitignore |
| Skill | 给 AI 编程助手的方法论指令 |

---

## 开始使用

```bash
cp -r path/to/strata/harness            ./harness
cp -r path/to/strata/browser-tests      ./browser-tests
cp -r path/to/strata/templates/features ./features
cp -r path/to/strata/templates/issues   ./issues
cat path/to/strata/gitignore.snippet >> .gitignore

cp -r path/to/strata/skills/static  .claude/skills/static
cp -r path/to/strata/skills/unit    .claude/skills/unit
cp -r path/to/strata/skills/browser .claude/skills/browser

./harness/testing.sh all
```

完整方法论（开发原则、Scenario 设计、Driver、开发范式）：[STRATA.md](STRATA.md)

---

## 参考文档

- [STRATA.md](STRATA.md) — 方法论全文
- [Scenario 格式规范](skills/browser/references/scenario-format.md)
- [Evidence 分类规则](skills/browser/references/evidence-taxonomy.md)
- [Browser 测试模型](skills/browser/references/harness-model.md)
