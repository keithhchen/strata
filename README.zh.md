# Strata

**得名于地质层理** — 层层叠加，共同讲述完整的故事。

[English](README.md)

> **知道它能用。不只是知道它被写了。**

---

AI 写代码的速度已经超过了你审查的速度。这就是问题所在。

不是写的问题——是知道的问题。知道写出来的东西是否真的能跑。知道它有没有把别的东西搞坏。知道，有凭有据地知道，这个功能做完了，而不只是"做完了"。

Strata 是为这个现实设计的测试方法论。三层测试。一套选层决策规则。还有 AI 编程助手 skill，把方法论编码进去，让你的 agent 做出和你最好的工程师一样的判断。

---

## 三层金字塔

核心洞察是："这个东西能用吗？"其实是三个不同成本级别的不同问题。

```
         ▲
        /B\        browser — 把产品当黑盒
       /   \       分钟级，需要运行中的产品
      /─────\
     /   U   \     unit — 纯逻辑
    /         \    秒级，无需服务器
   /───────────\
  /     S       \  static — 结构不变量
 /               \ 毫秒级，零依赖
/─────────────────\
```

**Static 问的是：结构还撑得住吗？** 无服务器、无导入、纯文本和 AST 分析，0.3 秒以内。这里住的是架构不变量——永远不该出现的模式、必须存在的文件、必须覆盖所有 case 的 handler。一个新路由绕过了 auth？static 在服务器启动之前就抓到了。

**Unit 问的是：逻辑是对的吗？** 无服务器、mock 外部依赖、5 秒以内。纯函数、解析器、状态机、权限规则。每一个 unit test 除了"它过了吗"还要回答另一个问题：*如果这个 test 挂了，产品上会坏什么？* 答案写在 docstring 里。一个没有 why 的测试，挂了就会被删掉而不是被修。

**Browser 问的是：产品能用吗？** 运行中的产品，当作黑盒，用真实浏览器驱动。不导入内部代码。不 mock 你要测试的东西。driver 像用户一样操作。证据——DOM 快照、日志、API 响应——提交到 git。截图留在本地。一次没有 committed 证据的 scenario run，等同于没跑过。

---

## 设计选择

**Driver 可以互换。** Scenario 是 markdown 文件。Playwright、browser-use、Claude in Chrome 是同一套 contract 的平级实现。切换 driver 不需要重写 scenario。

**Evidence 分类是强约束。** 文字证据（DOM、日志、JSON）commit 进 `browser-tests/reports/`。二进制证据（截图、视频）放在 `browser-tests/artifacts/`，gitignore。这让 repo 保持精简，同时不丢失可复现性。

**Tracking file 是契约。** 写代码之前，先写一个带测试计划的 tracking file。它从 `todo/` 移到 `done/` 的条件是：测试通过，证据存在。意图和证明和代码放在同一个地方。

**Skill 是可执行的方法论。** 三个 skill——`static`、`unit`、`browser`——不是文档，是指令。它们在你的 AI 助手内部运行。一个 agent 调用 static skill，做出的选层判断和你最好的工程师一样。方法论随 repo 走。

---

## 核心概念

| 概念 | 含义 |
|------|------|
| 层（Layer） | `static`、`unit` 或 `browser`——每层回答不同问题 |
| 不变量（Invariant） | 项目结构上必须永远成立的事实，写在 `static.py` 里 |
| Tracking file | 带测试计划的 markdown 文件，从 `todo/` 移到 `done/` |
| Scenario | 描述用户流程的 markdown 文件，与 driver 无关 |
| Driver | 执行 scenario 的工具：`playwright`、`browser-use`、`claude-in-chrome` |
| Evidence | 证明 scenario 通过或失败的东西——文字 commit，二进制留本地 |
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

完整方法论（开发原则、Scenario 设计、Driver、开发范式）：[HARNESS.md](HARNESS.md)

---

## 参考文档

- [HARNESS.md](HARNESS.md) — 方法论全文
- [Scenario 格式规范](skills/browser/references/scenario-format.md)
- [Evidence 分类规则](skills/browser/references/evidence-taxonomy.md)
- [Browser 测试模型](skills/browser/references/harness-model.md)
