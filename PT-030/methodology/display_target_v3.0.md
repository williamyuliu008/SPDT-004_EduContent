# display_target v3.0 拍板 (PT-030 methodology)

> **拍板日期**：2026-09-12
> **拍板来源**：共同仓 `docs/v3.0_approved.md` + `docs/migration/SPDT004_HANDOVER_PROMPT_v3.0_给刘宇.md`
> **拍板人**：雪薇 (用户)
> **影响范围**：所有 PT-030 真题卡 + 4 学科 zhenti JSON

---

## 一、v3.0 拍板内容

**雪薇端产卡默认 `display_target: ["学习中心"]`**

- ✅ 雪薇端产的所有 JSON 卡片默认渲染目标 = 学习中心
- ❌ 宇兄端负责 `["RUJING"]` 内容
- ❌ 不混合双目标 (避免渲染混乱)

## 二、字段说明

`display_target` 是 JSON 卡片中的渲染目标字段：

```json
{
  "card_id": "h2018_05",
  "schema_version": "v1.2",
  "display_target": ["学习中心"],
  "stem": "...",
  ...
}
```

| 值 | 含义 | 谁负责 |
|---|---|---|
| `["学习中心"]` | 雪薇端学习中心渲染 (本地 HTML) | 雪薇端 |
| `["RUJING"]` | 宇兄端 RUJING APP 客户端 | 宇兄端 |
| `["学习中心", "RUJING"]` | 双目标 (雪薇端 v3.0 暂不采用) | — |

## 三、雪薇端已补全数据

- **1355 个 JSON 卡片** display_target 已补全 (commit b89a0e9)
- 范围：145 数学 K 卡 + 30 数学方法论 + 5 政治方法论 + 49 专题 quiz + 1126 历史/地理/政治 cards/

## 四、commit 链

- `b89a0e9` — feat(cards): display_target 字段补全 — 雪薇端产出默认 `['学习中心']`
- `03c5c04` — feat(tools): display_target 补全脚本 (雪薇端 → `['学习中心']`) — 共同仓
- `_add_display_target.py` — 共同仓 tools/

## 五、立即可做

- **PT-030 雪薇端产的所有新卡** → 默认 `["学习中心"]`
- **宇兄端 RUjing 客户端** → `["RUJING"]` (雪薇端不参与)
- **历史 6 占位 + 政治 2 源空** → 补全后默认 `["学习中心"]`
- **2018 上海历史 v1.2 升级** → upgrade_pps_v11.py 跑完后补 display_target

## 六、相关文档

- 共同仓 `docs/v3.0_approved.md` (v3.0 总拍板)
- 共同仓 `docs/v3.0_draft.md` (v3.0 草稿)
- 共同仓 `docs/v3.0_h1_signoff.md` (H1 拍板)
- 共同仓 `docs/migration/SPDT004_HANDOVER_PROMPT_v3.0_给刘宇.md`
- 共同仓 `tools/_add_display_target.py` (补全脚本)
