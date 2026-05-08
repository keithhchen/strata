# Strata

**得名于地质层理** — 层层叠加，共同讲述完整的故事。

三个测试层。每层回答不同的问题。合在一起，证明你的软件是对的。

| 层 | 问题 | 成本 | 依赖 |
|----|------|------|------|
| **static** | 结构是否正确？ | < 0.3s | 无 |
| **unit** | 逻辑是否正确？ | < 5s | 无服务器 |
| **browser** | 产品是否正确？ | 分钟级 | 运行中的产品 |

AI 编程助手 skill 让这套方法论可复用——对人类开发者和 AI agent 同样有效。

---

## 快速开始

### 方案 A：从 template 新建项目

```bash
gh repo create my-app --template keithhchen/strata
cd my-app
```

### 方案 B：接入已有项目

```bash
# 1. 复制 harness 结构
cp -r path/to/strata/harness         ./harness
cp -r path/to/strata/browser-tests   ./browser-tests
cp -r path/to/strata/templates/features ./features
cp -r path/to/strata/templates/issues   ./issues

# 2. 追加 .gitignore 规则
cat path/to/strata/gitignore.snippet >> .gitignore

# 3. 安装 AI 助手 skills
cp -r path/to/strata/skills/static  .claude/skills/static
cp -r path/to/strata/skills/unit    .claude/skills/unit
cp -r path/to/strata/skills/browser .claude/skills/browser

# 4. 跑 starter 测试
./harness/testing.sh all
```

---

## 在 Web App 里使用 Strata

以 React + Express + PostgreSQL 项目为例。

### 第一步：想清楚你的不变量

写代码之前，先把"这个项目的结构有哪些铁律"写下来：

> "所有 Express 路由都必须经过 auth middleware。"  
> "所有 API handler 必须注册在 router index 里。"  
> "生产代码里不能有 `console.log`。"  
> "`.env.example` 必须记录 app 读取的所有环境变量。"

这些结构层面的事实放进 `harness/static.py`，不需要启动服务器就能检查。

### 第二步：先写失败的 static 测试

打开 `harness/static.py`，把你的不变量填进去：

```python
def test_routes_use_auth_middleware():
    """所有路由文件必须引入并应用 authMiddleware。

    If this fails: 有未受保护的路由被加入了。每个 endpoint
    都必须在处理请求前验证 JWT。
    """
    for path in ROOT.glob("src/routes/*.js"):
        src = path.read_text()
        assert "authMiddleware" in src, \
            f"{path.name} 必须应用 authMiddleware"
```

先跑一遍，**让它变红**：

```bash
./harness/testing.sh static
```

### 第三步：写纯逻辑的 unit 测试

找出不需要数据库或 HTTP 就能测试的逻辑：

- JWT 验证
- 输入校验
- 响应格式构建
- 查询参数解析
- 权限判断

每个测试都写清楚"这个 test 挂了，产品上会坏什么"：

```python
class TestJwtValidation:
    def test_expired_token_raises(self):
        """过期 token 必须被拒绝。

        If this fails: 已过期的 session 可以绕过认证，
        用户能读写他们已经无权访问的数据。
        """
        with pytest.raises(TokenExpiredError):
            verify_jwt(make_expired_token())
```

### 第四步：安装 skills，写第一个 browser scenario

```bash
cp -r path/to/strata/skills/static  .claude/skills/static
cp -r path/to/strata/skills/unit    .claude/skills/unit
cp -r path/to/strata/skills/browser .claude/skills/browser
```

复制 scenario 模板，描述第一个用户流程：

```bash
cp path/to/strata/templates/browser-tests/SCENARIO_TEMPLATE.md \
   browser-tests/scenarios/user-login.md
```

填写用户动作、观察点、断言。driver（Playwright、browser-use、Claude in Chrome）执行 scenario，scenario 文件本身与 driver 无关。

### 第五步：日常开发流程

```
新功能来了：
  1. 新建 features/todo/my-feature.md — 写测试计划，再动代码
  2. git add + commit 追踪文件
  3. git worktree add（或建分支）隔离开发
  4. 写测试 → 先让它红
  5. 写代码 → 让它绿
  6. ./harness/testing.sh all
  7. 跑 browser scenario，把 report commit 进 browser-tests/reports/
  8. mv features/todo/ → features/done/

Bug 来了：
  同上，用 issues/todo/ 替代 features/todo/
```

---

## 选层决策树

```
字符串模式、文件存在性、结构约定、依赖版本？
  → static

纯函数、解析器、状态机、确定性事件映射？
  → unit

API 响应、UI 渲染、数据库状态、文件状态、WebSocket 事件？
  → browser

改动涉及多个层？
  → 每层都测
```

原则：**优先用能回答问题的最低成本层。**

---

## AI Skills

Skills 是给 AI 编程助手（Claude Code、Codex、Cursor 等）的操作手册，把这套方法论编码进去。安装后，你的 AI 助手知道如何：

- 判断一个新测试属于哪一层
- 用 AST 或文本分析写 static 不变量检查
- 按 WHY 约定组织 unit 测试类
- 选择并执行 browser scenario
- 收集 evidence 并 commit 到正确的路径

**安装到 Claude Code：**

```bash
cp -r skills/static  .claude/skills/static
cp -r skills/unit    .claude/skills/unit
cp -r skills/browser .claude/skills/browser
```

**安装到 Codex：**

```bash
cp -r skills/static  .codex/skills/static
cp -r skills/unit    .codex/skills/unit
cp -r skills/browser .codex/skills/browser
```

---

## 项目结构

接入后你的项目新增：

```
your-project/
├── harness/
│   ├── static.py          # 结构不变量测试 — 按项目实际填写
│   ├── unit.py            # 纯逻辑测试 — 按项目实际填写
│   └── testing.sh         # ./harness/testing.sh [static|unit|all]
│
├── browser-tests/
│   ├── scenarios/         # 每个用户流程一个 .md 文件
│   ├── reports/           # 提交到 git 的文字证据（DOM、日志、JSON）
│   └── artifacts/         # 本地截图/视频（gitignored）
│
├── features/
│   ├── todo/              # 开发中的功能追踪文件
│   └── done/              # 已关闭的功能
│
└── issues/
    ├── todo/              # 开发中的 bug 追踪文件
    └── done/              # 已关闭的 bug
```

---

## 完成标准

一个改动完成，当且仅当：

1. 追踪文件记录了受影响的层
2. 测试在产品代码之前写（先让它红）
3. `./harness/testing.sh all` 全过
4. Browser scenario 有 commit 进 `browser-tests/reports/` 的 report 证据
5. 跳过的 browser 覆盖有明确的原因记录

---

## 参考文档

- [HARNESS.md](HARNESS.md) — 核心层级参考
- [Scenario 格式](skills/browser/references/scenario-format.md)
- [Evidence taxonomy](skills/browser/references/evidence-taxonomy.md)
- [Browser 模型](skills/browser/references/harness-model.md)
