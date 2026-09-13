# v1.1 数学板块闭环 SOP — 立体几何 + 导数实战手册

**版本**: v1.1
**日期**: 2026-09-13
**适用范围**: 立体几何 / 解析几何 / 导数 / 数列 / 概率统计 / 解三角形 6 大板块推进
**关联**: `D:/Z_学习平台/00-项目文档/0913_开发记录/总体开发计划_v1.1.md`

---

## 〇、SOP 总览

```
v1.1 板块闭环 = 7 步标准流程
Step 1: 盘点 (5 chain 模板 + _archive 备份)
Step 2: 母题入库 (K30-K34 等 5 母题)
Step 3: 链卡生成 (K01-K18 模板, v1.2.6 标准)
Step 4: 变形题字段 (related_zhenti/derived_from/derived_variants)
Step 5: 4 Tab sections.json (母题级 6-8 sections)
Step 6: main.json (chain 级知识链全景 v1.3.0)
Step 7: commit + push + handoff
```

**每步产出**:
- Step 1 → 现状报告 (哪些文件存在, 哪些缺失)
- Step 2 → 5 母题 + main.json 入仓
- Step 3 → 18 链卡入仓
- Step 4 → 每张母题 ≥ 3 道变形题引用
- Step 5 → 30-40 sections 追加
- Step 6 → main.json v1.3.0
- Step 7 → 1 commit (chain 完整) + 1 handoff

---

## 一、命名规范 (5 个 ID 体系)

### 1. 板块 chain 目录命名
- 中文, 与 chain 名一致
- 例: `projects/math/cards/线面平行证明/`, `projects/math/cards/导数/`

### 2. K 卡 ID 命名
- **板块内 chain 链卡**: `K01-K18` (固定 18 张, 每条 chain 独立)
- **板块母题**: `K30-K34` (导数) / `K10-K15` (立体几何) / `K20-K24` (解析几何) / `K40-K44` (数列) / `K50-K54` (概率统计) / `K60-K64` (解三角形)
- **变形题**: `K36-2~6` (导数) / `K16-2~6` (立体几何) / `K26-2~6` (解析几何) / `K46-2~6` (数列) / `K56-2~6` (概率统计) / `K66-2~6` (解三角形)
- 命名规则: `K母题号-子编号` (子编号从 2 开始, 1 留给主目录号)

### 3. card_id 命名
- v1 业务卡格式: `E-V1-{chain名}-{NN}` (NN = 01-18)
- 例: `E-V1-导数-01`, `E-V1-线面平行证明-15`

### 4. 方法论 ID 命名
- `M_{板块}_{NN}_{方法名}` (NN = 01-05)
- 例: `M_导数_01_单调性`, `M_立体_01_线面关系证明`

### 5. 91apu 真包 ID 命名
- `K_{板块}_{年份}{卷}_{题号}`
- 例: `K_导数_2018qg1_18`, `K_立体_2024qgjl_19`

---

## 二、文件结构 (每个板块统一)

```
projects/math/cards/{chain}/
├── K01.json          # 链卡 1
├── K02.json          # 链卡 2
├── ...
├── K18.json          # 链卡 18
├── K30.json          # 母题 1 (D-M1 单调性)
├── K31.json          # 母题 2 (D-M2 极值)
├── ...
├── K34.json          # 母题 5
├── K36-2.json        # 变形题 1
├── ...
├── K36-6.json        # 变形题 5
└── main.json         # chain 级知识链全景

projects/math/methods/{chain}/
├── M_{chain}_01_{方法名}.json
├── M_{chain}_02_{方法名}.json
├── ...
└── M_{chain}_05_{方法名}.json
```

---

## 三、Step 1: 盘点

### 1.1 检查 _archive 备份
```bash
ls _archive/2026-09-12_数学_K卡挂接_前/cards/{chain}/
```
如果备份存在 → 取回入库 (5 母题 + main.json 完整内容)
如果备份缺失 → 从 91apu 真包 + 学科知识生成

### 1.2 检查 HEAD 树现状
```python
import subprocess, json
for f in ['K30','K31','K32','K33','K34','main']:
    path = f'projects/math/cards/{chain}/{f}.json'
    try:
        subprocess.check_output(['git','show',f'HEAD:{path}'], encoding='utf-8')
    except subprocess.CalledProcessError:
        print(f'MISSING: {path}')
```

### 1.3 检查方法论
```bash
ls projects/math/methods/{chain}/
```
应该 5 张方法论 (M_{chain}_01~05)

### 1.4 检查 91apu 真包
```bash
ls apps/learning-hub-v2/_reader/_zhenti_sources/k_cards/{year}/K_{chain}_*.json
```
30 张真包题 (2018-2024 × 5-6 卷)

---

## 四、Step 2: 母题入库

### 2.1 从 _archive 取回 5 母题 + main.json
```powershell
$archive = '_archive\2026-09-12_数学_K卡挂接_前\cards\{chain}'
$dest = 'projects\math\cards\{chain}'
if (-not (Test-Path $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
foreach ($f in 'K30','K31','K32','K33','K34','main') {
  $src = Join-Path $archive "$f.json"
  $dst = Join-Path $dest "$f.json"
  if (Test-Path $src) { Copy-Item $src $dst -Force }
}
# 移除 Archive 属性
foreach ($f in 'K30','K31','K32','K33','K34','main') {
  $p = Join-Path $dest "$f.json"
  & cmd /c "attrib -A `"$p`"" 2>&1 | Out-Null
}
```

### 2.2 母题必备字段 (v1.2.6+ 标准)
```json
{
  "id": "K30",
  "type": "math_geometry_question",
  "maturity": "REVIEWED",
  "version": "1.2.6+",
  "schema": "v1.2.1",
  "subject": "math",
  "module": "{板块}",
  "topic": "{母题主题}",
  "source": "{真题来源/方法论归纳}",
  "url": "{91apu URL 或 null}",
  "verdict": "TRUE",
  "difficulty": "中档/难",
  "knowledge_points": [...],
  "front": "≥500 字 (题面+考点+方法)",
  "back": "≥1500 字 (答案+扣分点+变式)",
  "front_detail": "≥300 字",
  "back_detail": "≥1000 字",
  "tags": [...],
  "provenance": {...},
  "chain": "{板块}",
  "parent_cards": ["M_{chain}_0X_{方法名}"],
  "related_zhenti": [3 道 91apu 真包],
  "display_target": ["学习中心"],
  "method_ref": [可选],
  "card_id": "E-V1-{chain}-NN",
  "exam_type": "解答题",
  "frequency": 5,
  "scoring_points": [...],
  "common_mistakes": [...],
  "answer_template": "...",
  "back_core": "...",
  "svg_field": "{am1_母题.svg}",
  "replaces": "..."
}
```

### 2.3 Commit
```bash
git add projects/math/cards/{chain}/K30-K34 + main.json
git commit -m "card(math): M2 {chain}板块 5 母题入库 — K30-K34 + main.json (related_zhenti 3 道/张)"
```

---

## 五、Step 3: 链卡生成 (K01-K18)

### 3.1 18 张链卡分配模板 (按立体几何 5 chain 验证)
- **K01-K05**: 5 概念 (5 母题各对应 1 个核心概念)
- **K06-K09**: 4 方法 (G1-G4 4 大方法)
- **K10-K13**: 4 变式 (5 母题各 1 变式, 4 张省 1 张)
- **K14**: 1 错题归因 (5 类常见扣分)
- **K15**: 1 索引 (5 母题 × 难度 × 考频矩阵)
- **K16-K18**: 3 综合应用/考频/方法论索引

### 3.2 链卡必备字段 (v1.2.6 标准)
- **front**: ≥350 字符 (题型识别 + 答题模板 + 解题思路 + 高考识别信号)
- **back**: ≥1300 字符 (3 步标准动作 + 关键判定 + 5 类失分 + 方法论挂接 + 母题挂接 + 高考用法 + 典型真题 + 与本卡联系)
- **front_detail**: ≥300 字符
- **back_detail**: ≥800 字符 (方法论/母题挂接 + 高考用法详述 + 典型真题 + 变式题练习)
- **parent_cards**: 5 母题 (K30-K34)
- **method_ref**: 5 方法论 (M_{chain}_01~05)
- **related_zhenti**: 2-3 道 91apu 真包

### 3.3 批量生成脚本模板
参考 `tools/_gen_derivative_chain.py` 和 `tools/_expand_deriv_chains.py`:
- 18 张链卡定义在 `CARDS` 列表
- `gen_card(c)` 函数生成单张卡
- `main()` 写文件 + commit

### 3.4 Commit
```bash
git add projects/math/cards/{chain}/K01-K18.json
git commit -m "card(math): M2 {chain} chain 18 链卡入库 — K01-K18 (5 概念+4 方法+4 变式+1 错题+1 索引+3 综合)"
```

---

## 六、Step 4: 变形题字段

### 4.1 字段选择规则
- 母题**改自 91apu 真题**: 用 `derived_from: "K_{板块}_{年份}{卷}_{题号}"` (1 道)
- 母题**改自 v1 业务卡** (如 K10 中位线法): 用 `derived_variants: ["K16-2", "K16-3", ...]` (5+ 张)
- 母题**从 91apu 真题变形**: 用 `related_zhenti: ["K_{...}", ...]` (3+ 道)

### 4.2 每张母题至少 1 道变形题引用 (v1.1 1.4 硬要求)
- 优选: 3 道 related_zhenti + 1 derived_from
- 退化: 1 道 derived_from 或 1 道 related_zhenti

### 4.3 修字段 (Python 脚本)
```python
import subprocess, json
path = f'projects/math/cards/{chain}/K30.json'
out = subprocess.check_output(['git','show',f'HEAD:{path}'], encoding='utf-8')
d = json.loads(out)
d['related_zhenti'] = ['K_导数_2018qg1_18', 'K_导数_2020qg1_21', 'K_导数_2022qgyl_18']
with open(path, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
```

---

## 七、Step 5: 4 Tab sections.json

### 7.1 母题级 sections 结构 (6 张/母题)
每张母题 6 sections:
1. **tab-概念**: 母题核心概念 + 5 大 knowledge_points
2. **tab-方法**: 标准解法 3 步 (基于 K 卡 back 内容)
3. **tab-题型-综合 (变式空间)**: 5 方向变式
4. **tab-题型-综合 (与其他母题衔接)**: 4-5 张母题间衔接路径
5. **tab-辨析**: 3 类常见错误与修正
6. **tab-速查**: 母题速查矩阵 (卡 ID + 难度 + 来源 + 核心考点 + 变形题 + 方法论)

### 7.2 kp_id 命名
- `BOARD_{板块}_{母题号}`
- 例: `BOARD_导数_K30`, `BOARD_立体几何_K10`

### 7.3 sections.json 追加流程
```python
# 参考 tools/_gen_k30_k34_sections.py
import json
sections = json.load(open('apps/learning-hub-v2/_reader/数学/data/sections.json', encoding='utf-8'))
for mother in MOTHERS:
    # 6 sections per mother
    new_sections = generate_six_sections(mother)
    sections.extend(new_sections)
json.dump(sections, open('apps/learning-hub-v2/_reader/数学/data/sections.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
```

### 7.4 避免 kp_id 冲突
脚本中检查 `existing_kp_ids` 跳过已存在的 kp_id。

---

## 八、Step 6: main.json

### 8.1 main.json 模板 (v1.3.0)
```json
{
  "id": "main",
  "type": "chain_meta",
  "chain": "{板块}",
  "title": "{板块}·知识链全景",
  "version": "1.3.0",
  "schema": "v1.2.1",
  "maturity": "REVIEWED",
  "front": "...",
  "back": "v1.3.0 ... 5 母题 + 5 变形题 + 5 方法论 = 10 张 K 卡 100% 完整",
  "front_detail": "v1.3.0 母题+变形题双层闭环版知识链",
  "back_detail": "完整 5 母题状态矩阵...",
  "tags": [...],
  "provenance": {...},
  "display_target": ["学习中心"]
}
```

### 8.2 back 段必须包含
- 5 母题代码 (D-M1, D-M2, D-M3, D-M4, D-M5)
- 5 母题 → 5 方法论 映射
- 5 母题 → 15 道真包 (3 道/张)
- 母题衔接路径 (链式连接)
- v1.3.0 重大更新日志

---

## 九、Step 7: commit + push + handoff

### 9.1 commit message 规范
- `card(math): M2 {板块}板块 {动作} — {对象} ({指标})`
- `fix(derivative): M2 {板块} {问题} — {修复} ({指标})`
- `docs(数学): {版本} handoff — {内容}`

### 9.2 push 流程
```bash
git push origin main
git log origin/main --oneline -3
```

### 9.3 handoff 文档
路径: `D:/Z_学习平台/SPDT-004_EduContent/handoff/agent1_v1.1_m2_{chain}_done.md`

**handoff 内容模板**:
```
# Agent 1 → 全部窗口: v1.1 M2 路标点 — {板块}专题数据维度就绪
**日期**: {date}
**HEAD**: {hash} (knowledge-cards-prod main, 已 push)
**状态**: {板块}专题 {5 母题 + 18 链卡 + 5 方法论 + 40 sections} 全闭环
## 1. M2 {板块} 状态 (v1.1 1.5 验收)
| 项 | 状态 | 详情 |
## 2. 关键 commit 序列
## 3. 5 母题变形题引用
## 4. 18 链卡内容
## 5. 给 3-UI 窗口的接力
## 6. M2 下一阶段
```

### 9.4 commit + handoff 推送
```bash
cd D:/Z_学习平台/SPDT-004_EduContent
git add handoff/agent1_v1.1_m2_{chain}_done.md
git commit -m "handoff(agent1): M2 {板块}专题数据维度就绪 - {关键指标} (HEAD {hash})"
git push origin master
```

---

## 十、检查清单 (每步验收)

### Step 1 检查
- [ ] `_archive/2026-09-12_数学_K卡挂接_前/cards/{chain}/` 备份存在
- [ ] `projects/math/cards/{chain}/` 目录在 HEAD 中存在/缺失确认
- [ ] `projects/math/methods/{chain}/` 5 张方法论齐全
- [ ] `apps/learning-hub-v2/_reader/_zhenti_sources/k_cards/{year}/K_{chain}_*.json` 30 张真包齐全

### Step 2 检查
- [ ] 5 母题 K30-K34 (或 K10-K15 等) maturity=REVIEWED
- [ ] 5 母题 each has related_zhenti 3 道引用
- [ ] 5 母题 each has parent_cards 指向 1 张方法论
- [ ] main.json 存在, version=v1.3.0
- [ ] 1 commit (含 main.json)

### Step 3 检查
- [ ] 18 链卡 K01-K18 all maturity=REVIEWED
- [ ] 18 链卡 front ≥350 字符
- [ ] 18 链卡 back ≥1300 字符 (扩充后)
- [ ] 18 链卡 parent_cards 指向 5 母题
- [ ] 18 链卡 method_ref 指向 5 方法论
- [ ] 18 链卡 related_zhenti 2-3 道真包
- [ ] 1 commit (18 文件)

### Step 4 检查
- [ ] 5 母题 each has 至少 1 道变形题引用 (related_zhenti OR derived_from OR derived_variants)

### Step 5 检查
- [ ] sections.json 含 5 母题级 sections (6 张/母题 = 30 sections)
- [ ] 30 sections 覆盖 tab-概念/tab-方法/tab-题型-综合(2)/tab-辨析/tab-速查
- [ ] kp_id 用 `BOARD_{板块}_{母题号}` 命名

### Step 6 检查
- [ ] main.json version=v1.3.0
- [ ] main.json back 段含 5 母题 + 5 变形题 + 5 方法论完整状态矩阵
- [ ] main.json tags 含 "M2 路标达成"

### Step 7 检查
- [ ] 1 commit (母题) + 1 commit (链卡) + 1 commit (back 扩充) + 1 commit (main.json v1.3.0) 已 push
- [ ] 1 handoff 文档已 commit + push 到 SPDT-004_EduContent master

---

## 十一、常见错误 (P0 必须避免)

| 错误 | 症状 | 修复 |
|---|---|---|
| 1. 推 4 板块 K 卡到 active 路径 | 违反"立体几何交付前不开其他板块"约束 | 用 `git revert` 撤回; 严重时 force push |
| 2. 母题 K 卡 front < 500 字 | 内容不充实, 4 Tab 显示空洞 | 重写 front 段, 加 5 大概念 + 题型识别 + 答题模板 |
| 3. 链卡 back < 1300 字 | 深度解析缺失 | 跑 `tools/_expand_deriv_chains.py` 通用扩展脚本 |
| 4. 母题缺 related_zhenti | 违反 v1.1 1.4 硬要求 | 补 3 道 91apu 真包引用 |
| 5. chain 目录命名错误 | 链卡找不到 chain 归属 | 保持中文 chain 名, 与 `chain` 字段一致 |
| 6. K 卡 ID 重复 | 同名 K 卡冲突 | 每条 chain 独立 K01-K18, 母题用 K30-K34 等独立号段 |
| 7. sections.json kp_id 重复 | 写入时 overwrite 已有 sections | 脚本检查 existing_kp_ids, 跳过已存在 |
| 8. python 脚本 emoji 报错 | PowerShell GBK 编码崩溃 | emoji 改 ASCII (WARN/OK/ERROR) |
| 9. 工作树 .gitignore 误排除 | commit 后 git status 不显示 | `git check-ignore -v <path>` 检查 |
| 10. commit 引用错乱 (其他 agent 推) | push 失败, 需先 pull | `git pull --rebase` 同步, 再 push |

---

## 十二、自动化脚本清单 (tools/)

| 脚本 | 作用 |
|---|---|
| `_gen_derivative_chain.py` | 导数 18 链卡批量生成 (Step 3) |
| `_expand_deriv_chains.py` | 18 链卡 back 内容扩充 (Step 3 验收修复) |
| `_gen_k10_k15_sections.py` | K10-K15 母题级 sections 生成 (Step 5) |
| `_gen_k30_k34_sections.py` | K30-K34 母题级 sections 生成 (Step 5) |
| `_check_*.py` | 各种字段检查工具 |
| `_audit_3d_derivative.py` | 立体几何 + 导数板块审核 (Step 1) |

---

## 十三、文件路径速查

```
# 知识库仓
D:\Z_学习平台\knowledge-cards-prod\
  apps\learning-hub-v2\_reader\_zhenti_sources\k_cards\{year}\K_{板块}_{年卷}_{题号}.json  # 91apu 真包
  projects\math\cards\{chain}\  # K 卡目录
  projects\math\methods\{chain}\  # 方法论
  apps\learning-hub-v2\_reader\数学\data\sections.json  # 4 Tab 数据
  tools\_*.py  # 自动化脚本

# 共同仓
D:\Z_学习平台\SPDT-004_EduContent\
  handoff\agent1_v1.1_m2_{chain}_done.md  # handoff 文档

# 文档仓
D:\Z_学习平台\00-项目文档\
  0913_开发记录\总体开发计划_v1.1.md
  数学_3agent_任务分配_v1.0.md
```

---

## 十四、M2 推进时间预估 (基于实战数据)

| 步骤 | 时间 | 备注 |
|---|---|---|
| Step 1 盘点 | 5 分钟 | 看 HEAD 树 + _archive 备份 |
| Step 2 母题入库 | 5 分钟 | copy + commit |
| Step 3 链卡生成 | 30 分钟 | 写脚本 + 18 张卡 |
| Step 3.5 链卡 back 扩充 (修复) | 10 分钟 | 通用扩展脚本 |
| Step 4 变形题字段 | 5 分钟 | 编辑 K 卡 |
| Step 5 4 Tab sections | 20 分钟 | 写脚本 + 30 sections |
| Step 6 main.json | 5 分钟 | 写 v1.3.0 |
| Step 7 commit + handoff | 10 分钟 | 4-5 commit + 1 handoff |
| **总计** | **~90 分钟** | M2 单板块完整闭环 |

---

## 十五、M2 验收模板 (v1.1 1.5)

每板块需满足:
- [ ] 5 母题 maturity=REVIEWED + related_zhenti ≥ 3 道
- [ ] 18 链卡 maturity=REVIEWED + parent_cards/method_ref/zhenti_or_derived 全
- [ ] 5 方法论 maturity=REVIEWED v1.2.6
- [ ] main.json v1.3.0 + 5 母题 + 5 变形题 + 5 方法论状态矩阵
- [ ] sections.json 30 母题级 sections (6/母题)
- [ ] 1 commit + 1 handoff 已 push

满足以上 6 项 → 板块数据维度闭环 → 通知 3-UI 雪薇验收。

---

**SOP 完。如有问题或需要调整, 联系 Mavis (root session)。**
