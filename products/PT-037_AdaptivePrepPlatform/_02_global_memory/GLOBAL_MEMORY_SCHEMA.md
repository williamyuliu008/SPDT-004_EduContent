# 全局记忆体数据结构

> 版本: v1.0 | 数据库: PostgreSQL + Neo4j + InfluxDB + Redis | 适用: PT-037

---

## 一、PostgreSQL — 用户画像 + 错题剧本

### 用户画像表 (user_profile)

```sql
CREATE TABLE user_profile (
    user_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nickname         VARCHAR(100),
    grade            VARCHAR(50),          -- 高三 / 高二
    target_exam      VARCHAR(200),         -- 国美书法校考 / 高考
    active_packs     TEXT[],               -- 当前激活的配置包列表
    created_at       TIMESTAMP DEFAULT NOW(),
    updated_at       TIMESTAMP DEFAULT NOW()
);
```

### 用户状态表 (user_state) — S/C/F/I 四维实时状态

```sql
CREATE TABLE user_state (
    user_id          UUID PRIMARY KEY REFERENCES user_profile(user_id),
    S_score          NUMERIC(5,2) DEFAULT 0,  -- 掌握度 0-100
    C_cognitive_load NUMERIC(3,1) DEFAULT 1,  -- 认知负荷 1-10
    F_fatigue        NUMERIC(4,1) DEFAULT 0, -- 疲劳值 0-∞
    I_interest       NUMERIC(3,1) DEFAULT 5,  -- 兴趣指数 1-10
    last_active      TIMESTAMP DEFAULT NOW(),
    -- 每日重置: F 每晚清零；C/I 由Agent5实时更新
    CONSTRAINT check_S CHECK (S_score BETWEEN 0 AND 100),
    CONSTRAINT check_C CHECK (C_cognitive_load BETWEEN 1 AND 10),
    CONSTRAINT check_I CHECK (I_interest BETWEEN 1 AND 10)
);
```

### 知识点掌握表 (knowledge_mastery)

```sql
CREATE TABLE knowledge_mastery (
    user_id      UUID REFERENCES user_profile(user_id),
    kb_id        VARCHAR(50),              -- 知识条目ID
    pack_id      VARCHAR(50),              -- 配置包ID
    S_score      NUMERIC(5,2) DEFAULT 0,  -- 该知识点的掌握度
    last_tested  TIMESTAMP,
    times_tested INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, kb_id)
);
```

### 错题剧本表 (error_script)

```sql
CREATE TABLE error_script (
    script_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES user_profile(user_id),
    kb_id         VARCHAR(50),            -- 关联知识点
    pack_id       VARCHAR(50),
    question_id   VARCHAR(50),             -- 题目ID
    error_type    VARCHAR(100),            -- 错误类型
    wrong_answer  TEXT,
    correct_answer TEXT,
    script_text   TEXT,                    -- 错题剧本正文
    created_at    TIMESTAMP DEFAULT NOW(),
    review_count  INTEGER DEFAULT 0,
    mastery_score NUMERIC(5,2) DEFAULT 0  -- 复习后掌握度
);
```

---

## 二、Neo4j — 知识图谱

### 节点类型

```cypher
// 知识条目节点
(:KnowledgeNode {
    kb_id: String,           -- 唯一ID
    pack_id: String,         -- 所属配置包
    concept: String,         -- 概念名称
    definition: String,      -- 定义
    bloom_level: String,     -- 认知层级
    frequency: String,       -- 考频星级
    status: String           -- P0/P1/P2
})

// 配置包节点
(:SubjectPack {
    pack_id: String,
    name: String,
    status: String
})

// 能力节点
(:Ability {
    ability_id: String,
    name: String
})
```

### 关系类型

```cypher
// 知识点依赖关系
(k1:KnowledgeNode)-[:PREREQUISITE]->(k2:KnowledgeNode)   -- 前置
(k1:KnowledgeNode)-[:RELATED]->(k2:KnowledgeNode)         -- 相关
(k1:KnowledgeNode)-[:LEADS_TO]->(k2:KnowledgeNode)        -- 后置

// 知识点-能力关系
(k:KnowledgeNode)-[:TRAINS]->(a:Ability)                  -- 训练
(k:KnowledgeNode)-[:BELONGS_TO]->(p:SubjectPack)          -- 属于

// 跨包关联
(k1:KnowledgeNode)-[:CROSS_PACK {target_pack: String}]->(k2:KnowledgeNode)
```

### 示例查询

```cypher
// 查询某知识点的全部前置知识
MATCH (k:KnowledgeNode {kb_id: 'KB_CAFA_颜真卿'})-[:PREREQUISITE*]->(pre)
RETURN pre.kb_id, pre.concept

// 查询跨包关联
MATCH (k1:KnowledgeNode)-[r:CROSS_PACK]->(k2)
WHERE k1.pack_id = 'cafa_calligraphy_2026'
RETURN k1.concept, k2.concept, r.target_pack
```

---

## 三、InfluxDB — 学习轨迹（时序数据）

### 测量: study_sessions

```
tags: user_id, pack_id, agent_type, question_type
fields: 
  - duration_seconds (integer)
  - score (float)
  - cognitive_load (float)
  - fatigue_delta (float)
  - interest_delta (float)
timestamp: session_end_time
```

### 测量: agent_calls

```
tags: user_id, agent_id, action_type, pack_id
fields:
  - response_time_ms (integer)
  - tokens_used (integer)
  - success (boolean)
timestamp: call_time
```

---

## 四、Redis — 系统配置缓存

| Key | 类型 | 用途 | TTL |
|-----|------|------|-----|
| `active_packs:{user_id}` | SET | 用户当前激活的配置包 | 24h |
| `daily_quota:{user_id}` | HASH | 每日学习配额 | 24h |
| `agent_state:{agent_id}` | HASH | Agent调度状态 | 10min |
| `cross_pack_cache:{pack_id}` | JSON | 跨包联动关系缓存 | 1h |

---

## 五、数据流总览

```
用户行为
    │
    ▼
Agent5 调度决策 → 更新 Redis（状态）
    │
    ├─→ Agent4 训练 → PostgreSQL（错题剧本）
    │
    ├─→ Agent2 审计 → Neo4j（图谱更新）
    │
    └─→ Agent3 可视化 → InfluxDB（轨迹）+ 读取 PostgreSQL/Neo4j
```
