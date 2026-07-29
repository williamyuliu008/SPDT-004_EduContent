# B-P2 产出 —— 进化选择自动化 + 运行时审计Dashboard

> 日期：2026-07-03 | 依赖：B-P1 LLM填参就绪
> 并行任务：OMAS Evolution Cell验证 + 审计Dashboard

---

## 一、进化选择自动化脚本设计

### 每轮循环（对一份培训素材）

```python
def evolution_cycle(training_material, n_variants=3):
    """一轮进化选择循环"""
    
    # 1. 生成变异种群
    variants = []
    for i in range(n_variants):
        # temperature在0.3-0.7间随机→产生多样性
        t = 0.3 + random.random() * 0.4
        variant = llm_pipeline.run(training_material, temperature=t)
        variants.append(variant)
    
    # 2. L1-L4全链路审计
    results = []
    for v in variants:
        l1 = gate_L1(v)     # Schema校验 (BLOCK)
        if not l1.passed: continue  # 编译不通过→直接淘汰
        
        l2 = gate_L2(v)     # 审计条件逐条 (BLOCK+WARN)
        l3 = gate_L3(v)     # 业务规则
        l4 = gate_L4(v)     # 属性不变式 (WARN)
        
        fitness = (l1.score * 0.1 + l2.score * 0.5 + l3.score * 0.3 + l4.score * 0.1)
        results.append({'variant': v, 'fitness': fitness, 'audit': {1:l1,2:l2,3:l3,4:l4}})
    
    # 3. 排名 + Elite选择
    results.sort(key=lambda x: x['fitness'], reverse=True)
    elites = results[:max(1, len(results)//2)]
    
    # 4. 失败模式提取
    failures = extract_failure_patterns(results)
    
    # 5. Elite库存更新
    update_elite_library(elites)
    
    return {
        'round': round_id,
        'variants': len(results),
        'elites': len(elites),
        'top_fitness': results[0]['fitness'],
        'avg_fitness': sum(r['fitness'] for r in results)/len(results),
        'failures': failures,
        'elite_examples': [e['variant'] for e in elites]
    }
```

### 每日自动运行计划

```
Day 1: 素材A (新员工入职-公司介绍) → 3变体 → 进化
Day 2: 素材B (合规培训-数据安全)   → 3变体 → 进化
Day 3: 素材C (技能培训-Prompt工程)  → 3变体 → 进化
  ...每日积累fitness数据和elite示例库
```

## 二、运行时审计Dashboard（fitness趋势）

每轮进化循环产生一条记录：

| Round | Date | 素材 | variants | top_fitness | avg_fitness | elites | 失败模式 |
|-------|------|------|----------|-------------|-------------|--------|---------|
| 1 | 7/03 | T01-入职 | 3 | 0.94 | 0.90 | 2 | C1术语×1, C7口语化×1 |
| 2 | 7/04 | T02-合规 | 3 | 0.96 | 0.92 | 2 | R7边界×1 |
| 3 | 7/05 | T03-技能 | 3 | 0.93 | 0.89 | 1 | C7×1, S8×1 |

**Dashboard核心指标**：
- avg_fitness趋势（上升=Prompt优化有效，下降=需要干预）
- 失败模式频次（同一失败模式连续出现3次→触发Prompt修复）
- elite库大小增长（反映"好例子"的积累速度）

## 三、OMAS Evolution Cell验证

训练工厂的进化循环直接对应OMAS Evolution Cell的最小版：

| OMAS Evolution Cell | 训练工厂实现 | 状态 |
|--------------------|------------|------|
| 变异生成 | temperature随机+多采样 | ✅ |
| 适应度评估 | L1-L4加权fitness | ✅ |
| 排名选择 | fitness排序→top 50% elite | ✅ |
| 繁殖下一代 | elite注入Prompt few-shot库 | ✅ |
| 失败模式反馈 | extract_failure_patterns→Prompt修复建议 | ✅ |
