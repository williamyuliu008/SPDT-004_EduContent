# R-002 规则 —— JSON→渲染器参数映射必须确定性

> 日期：2026-07-04 | 来源：DRAM视频V1批量渲染3类bug

---

## 规则

**JSON→style_guide函数参数的映射逻辑，必须通过类型注册表（MAPPER dict）实现，禁止ad-hoc的if/else分支。**

具体约束：
1. 每种scene_type对应一个独立的mapper函数，签名统一为 `(scene_json) → (func_name, params_dict)`
2. mapper函数内部的数据提取逻辑必须**显式声明来源字段**，不允许"试试这个字段不行再试那个"
3. 新增scene_type时，新增mapper函数并注册到MAPPER dict——不修改现有mapper
4. mapper函数的正确性必须通过单元测试验证（针对每种scene_type的典型JSON→预期参数验证）

## 为什么R-001不够

R-001只约束了"渲染API层"（必须用style_guide函数，不准裸用Manim API）。

但R-001没有约束"数据映射层"——即从Scene JSON中提取哪些字段、以什么格式传递给style_guide函数的转换逻辑。T02的bug出在渲染层（裸用Manim），DRAM V1的bug出在映射层（ad-hoc的字段解析）。

**两层都需要确定性约束。**

## V1→V2的关键修正

| V1问题 | 根因 | V2修正 |
|--------|------|--------|
| comparison_table维度列为空 | `rows.append(['', wrong, right])`——维度列硬编码为空字符串 | `map_contrast()`从wrong_text行中解析"："分隔符提取维度名 |
| 3:27文字漂移 | 部分contrast场景走`layout_contrast`的回退逻辑 | 统一走`comparison_table`输出格式 |
| diagram场景文字不居中 | `box_diagram`调用正确，但部分scene的JSON未提供nodes字段→回退到term_card | 回退是正确行为——不强制注入数据到不匹配的渲染函数 |

## 与CGM原则的对应

这条规则的本质就是CGM支柱3（参数化接口）在渲染管线中的体现：**Scene JSON到style_guide函数的转换=一种"参数填充"操作**，需要在Schema（MAPPER注册表）的约束下进行，不能自由发挥。
