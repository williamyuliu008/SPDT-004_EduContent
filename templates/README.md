# templates/ · L0_stable · Agent 模板库

> **Layer**: L0_stable（受 W_low 保护）
> **依据**: [LAYERS.md](../LAYERS.md) + [WINDOWS.md](../WINDOWS.md) + [SPDT.yaml](../SPDT.yaml)
> **状态**: 已稳定 / 早期产物

---

## 定位

Agent 协作模板库——定义"如何组织多个 Agent 一起工作"的模式。

## 模板清单

| 模板 ID | 名称 | 用途 |
|:---|:---|:---|
| `M1_mobile_first` | 移动优先 | 移动端优先的 Agent 配置 |
| `T1_coop_sequential` | 顺序协作 | Agent 链式串行 |
| `T2_coop_parallel` | 并行协作 | Agent 多路并行 |
| `T3_game_adversarial` | 对抗博弈 | 攻防对抗（如 Gen+Critic） |
| `T4_game_collaborative` | 协作博弈 | 多个 Agent 协作求解 |
| `T5_hybrid_complex` | 混合复杂 | 多种模式混合 |
| `T6_content_pipeline` | 内容管线 | 内容生产专用 |
| `T7_data_terminal` | 数据终端 | 数据查询专用 |
| `T8_knowledge_engine` | 知识引擎 | 知识库驱动 |

## 公共组件

`_common/`：
- `ci_template.yml` — CI 模板
- `deploy_template.md` — 部署模板
- `dlv_common_bridge.py` / `_agent_os_bridge.py` — 桥接器

## 与 L1/L2 的关系

- **消费方（L1/L2）**: 任何需要"多 Agent 协作"的模块
- **被消费方**: 无（L0 是底层）

## 改动窗口

- 仅 **W_low**（稳定维护窗）
- 任何改动需走 RFC（哪怕 1 行）

## 引用

- 上层: [SPDT.yaml](../SPDT.yaml) 中 pdt_id=`AgentTemplates`
