# 智能体接入SOP v1.0

> SPDT-001 · Phase 2 产出 | 新APP接入智能体框架标准化流程
> 鸿蒙特使 🏗️ | 2026-07-18

---

## 前置条件

- APP 基于 `common/` 内核模板生成 (init-app.ps1)
- DevEco 6.1.1 环境 (DEVECO_SDK_HOME + OHOS_BASE_SDK_HOME)
- 小龙虾 mock server 已启动 (`localhost:8848`)

---

## 接入步骤（6步 · 预计 0.5-1天）

### 步骤 1: 声明 task_type

APP 向小龙虾注册自己的任务类型：

```bash
curl -X POST http://localhost:8848/api/v1/app/register \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "thinkkit-coach",
    "app_name": "ThinkKit Coach",
    "task_types": ["recommend_plan", "generate_questions"],
    "content_schemas": ["plans", "questions"]
  }'
```

### 步骤 2: 更新 STORAGE_KEYS

在 `entry/src/main/ets/common/storage/keys.ts` 中添加 agent 存储键（如果从模板生成且未添加）：

```typescript
// 追加到 STORAGE_KEYS
AGENT_PROFILE: 'AGENT_PROFILE',
AGENT_MASTERY: 'AGENT_MASTERY',
CONTENT_MANIFEST: 'CONTENT_MANIFEST',
```

### 步骤 3: 复制 agent-core 到 APP

```powershell
# 从 SPDT 共享目录复制到 APP
Copy-Item "D:\92_products\SPDT-001_Harmony\common\agent-core\*.ets" `
    "D:\92_products\SPDT-001_Harmony\apps\my-app\entry\src\main\ets\common\agent\"
```

### 步骤 4: 导入并初始化 AgentEngine

```typescript
// entry/src/main/ets/pages/Index.ets
import { AgentEngine, AgentConfig, AgentDimension, Insight, RecommendedAction } from 'common/agent-core';
```

初始化（在 `aboutToAppear()` 中）：

```typescript
private agent: AgentEngine = new AgentEngine({
  appId: 'thinkkit-coach',                 // 修改为实际 app_id
  lobsterBaseUrl: 'http://localhost:8848/api/v1',
  mockMode: true,                          // Phase 2 mock → Phase 3 真实
  dimensions: ['A','B','C','D','G']        // 按需选择维度
});

async aboutToAppear(): Promise<void> {
  await this.agent.init();
  if (!this.agent.isColdStartComplete()) {
    this.agent.startColdStart();
  }
}
```

### 步骤 4: 最小接入 — 面板洞察

最快速的集成方式是添加洞察卡片：

```typescript
@Builder buildDashboard() {
  Column() {
    // ... 现有仪表板内容 ...

    // 智能体洞察
    if (this.insights.length > 0) {
      Column() {
        Text('🧠 智能洞察').fontSize(14).fontWeight(600)
        ForEach(this.insights, (ins: Insight) => {
          Row() {
            Text(ins.title).fontSize(13).fontWeight(600)
            Text(ins.description).fontSize(11).fontColor('#888')
          }
        })
      }.padding(14).backgroundColor('#F0FFF4').borderRadius(10)
    }
  }
}
```

刷新洞察的方法：

```typescript
refreshInsights(): void {
  this.insights = this.agent.generateInsights(
    this.agent.getProfile().weaknesses,
    this.agent.getProfile().strengths,
    this.agent.getProfile().errorAttribution.conceptual,
    this.agent.getProfile().errorAttribution.calculative,
    0.6  // 近期正确率
  );
}
```

### 步骤 5: 接入小龙虾出题

```typescript
askLobster(): void {
  this.agent.lobster.generateQuestions('math', 2, 5)
    .then((questions: object[]) => {
      this.questions = questions;
    });
}
```

### 步骤 6: 编译验证

```bash
cd D:\92_products\SPDT-001_Harmony\apps
python build_any.py thinkkit-coach --deploy
```

---

## 维度选择指南

| APP 类型 | 推荐维度 | 最小维度 |
|:---|:---|:---|
| 学习辅导类 | A+B+C+D+E+G+H | A+G |
| 内容工具类 | A+E+G | G |
| 习惯追踪类 | A+B+H | A+H |
| 开发者工具类 | D+G | G |

---

## 接入检查清单

- [ ] `app_id` 已向小龙虾注册 (`POST /app/register`)
- [ ] STORAGE_KEYS 包含 AGENT_PROFILE / AGENT_MASTERY
- [ ] AgentEngine 已初始化 (aboutToAppear)
- [ ] 冷启动流程已集成（或显式跳过）
- [ ] 面板Tab显示智能洞察卡片
- [ ] 小龙虾 /task 接口可调用（mock或真实）
- [ ] 编译+签名+部署通过
- [ ] 真机端到端验证 (build_any.py --deploy)

---

> 🏗️ 智能体接入SOP v1.0 | 目标: 新APP <1天接入
