# 4 主题 12 道 LLM 新母题 — 2026-09-13 08:34

> **生成工具**: `python -m pt030_toolkit.cli llm-gen "<theme>" --count 3 --subject 数学`
> **模型**: glm-4-flash (实际)
> **API**: $env:ZHIPU_API_KEY = dfe1418d08b54255bb46f7e70cf96b99.IuQdU4ak2mIKqIGK
> **入库**: `D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\llm_gen\<主题>\`

---

## 一、4 主题选题理由

| 主题 | 现有 K 卡密度 | llm-gen 补充 | 板块 |
|---|---:|---:|---|
| **解三角形** | 12 张 (最稀) | 3 道 | 解三角形 |
| **概率统计** | 22 张 (次稀) | 3 道 | 概率统计 |
| **数列** | 24 张 (中等) | 3 道 | 数列 |
| **立体几何** | 27 张 (密) | 3 道 | 立体几何 |

**策略**: 优先补全薄弱板块 (解三角形/概率统计), 中等板块 (数列), 验证密板块 (立体几何) 题目质量

---

## 二、解三角形 (3 道)

### Q1: ∠A=60°, ∠B=45°, AC=5, 求 BC
```json
{
  "q_no": 1,
  "stem": "在三角形ABC中，已知∠A=60°，∠B=45°，边AC=5，求边BC的长度。",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "answer": "A",
  "explanation": "利用正弦定理求解，sinB/sinC = b/c，代入已知条件求解得b=5√2。",
  "knowledge_points": ["正弦定理"],
  "variant_direction": "改条件为不同角度, 检验正弦定理应用"
}
```

### Q2: a=8, b=10, c=12, 求 sinA
```json
{
  "q_no": 2,
  "stem": "已知 a=8, b=10, c=12, 求角 A 的正弦值。",
  "answer": "C",
  "explanation": "余弦定理求 cosA, sin²+cos²=1 求 sinA",
  "knowledge_points": ["余弦定理", "同角三角函数基本关系"]
}
```

### Q3: 略

---

## 三、概率统计 (3 道)

### Q1: 50 学生, 男 60%/女 40%, 抽 3 人恰好 2 女
```json
{
  "q_no": 1,
  "stem": "某班50名学生中, 男生60%, 女生40%, 随机抽3人, 求恰好2女概率。",
  "answer": "B",
  "explanation": "C(20,2)*C(30,1)/C(50,3)",
  "knowledge_points": ["古典概型", "组合"]
}
```

### Q2: 甲乙袋, 数字之和 = 6 概率
```json
{
  "q_no": 2,
  "stem": "甲袋 1-5, 乙袋 1-3, 各抽 1 球, 数字之和 = 6 概率",
  "answer": "B",
  "explanation": "5*3=15 总, (1,5)(2,4) = 2 种, P=2/15",
  "knowledge_points": ["古典概型", "枚举"]
}
```

### Q3: 略

---

## 四、数列 (3 道)

### Q1: 等差 {a_n}, a_1+a_4=10, a_2+a_3=14, 求 a_5
```json
{
  "q_no": 1,
  "stem": "等差 {a_n}, a_1+a_4=10, a_2+a_3=14, 求 a_5",
  "answer": "C",
  "explanation": "列方程组求 d 和 a_1, 推出 a_5"
}
```

### Q2: b_n = 2^n - 1, 求 S_n
```json
{
  "q_no": 2,
  "stem": "b_n = 2^n - 1, 求 S_n",
  "answer": "A",
  "explanation": "错位相减法"
}
```

### Q3: 略

---

## 五、立体几何 (3 道)

### Q1: 正方体 A1D1 与 CD 异面角
```json
{
  "q_no": 1,
  "stem": "正方体 ABCD-A1B1C1D1, AB=2, 异面直线 A1D1 与 CD 角",
  "answer": "C",
  "explanation": "异面角 = 60° (正方体棱角)"
}
```

### Q2: 圆锥侧面积
```json
{
  "q_no": 2,
  "stem": "圆锥 P-AB, 底面半径 r, 高 h, 侧面积 S",
  "answer": "C",
  "explanation": "S=πrl, l=√(r²+h²)"
}
```

### Q3: 略

---

## 六、入库

- **位置**: `D:\Z_学习平台\knowledge-cards-prod\projects\math\cards\本地上海\PT030_2026-09-13\llm_gen\`
- **schema**: K_card v1.2.1
- **maturity**: DRAFT (LLM 生成需人工 review)
- **display_target**: ["学习中心"]
- **provenance.type**: "llm_gen", "source": "glm-4-flash"

---

## 七、立即可做

- **人工 review 12 道母题**: 筛选有价值的, 入正式 4 步法数学卡库
- **每主题再跑 5-10 道**: 用 llm-gen 扩展薄弱板块
- **变式推演**: llm-review 给每道加 variants/difficulty

---

**作者**: 雪薇端 (mavis 学生助手)
**生成时间**: 2026-09-13 08:34 (cron 8 min 跑完 4 主题)
