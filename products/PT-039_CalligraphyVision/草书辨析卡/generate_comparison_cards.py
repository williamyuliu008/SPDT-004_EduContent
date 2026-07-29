#!/usr/bin/env python3
"""
草书辨析卡 Prompt 提取脚本
从 calligraphy_visual_ontology.yaml 提取辨析对 Prompt，输出到 prompts/
"""
import re, os
from pathlib import Path

ONTOLOGY = Path(__file__).parent.parent / "书法视觉本体库" / "calligraphy_visual_ontology.yaml"
OUT_DIR = Path(__file__).parent
OUT_DIR.mkdir(exist_ok=True)

def extract_section(yaml_text, section_name):
    """提取 YAML 中某个键下的所有条目"""
    lines = yaml_text.split('\n')
    results = {}
    current_key = None
    in_section = False
    indent_level = 0
    buffer = []

    for line in lines:
        if line.strip().startswith(section_name + ':'):
            in_section = True
            indent_level = len(line) - len(line.lstrip())
            continue
        if in_section:
            stripped = line.strip()
            if stripped.startswith('- id:'):
                if current_key and buffer:
                    results[current_key] = '\n'.join(buffer)
                current_key = stripped.replace('- id:', '').strip()
                buffer = [line]
            elif stripped.startswith(section_name.replace('_', ' ').title() + ':') and not stripped.startswith('-'):
                if current_key and buffer:
                    results[current_key] = '\n'.join(buffer)
                break
            elif stripped and not line.startswith(' ' * (indent_level + 1)) and current_key:
                if current_key and buffer:
                    results[current_key] = '\n'.join(buffer)
                break
            else:
                buffer.append(line)
    if current_key and buffer:
        results[current_key] = '\n'.join(buffer)
    return results


def extract_pairs_from_ontology():
    """从 ontology 提取 grass_script_discrimination 辨析对"""
    text = ONTOLOGY.read_text(encoding='utf-8')

    # 提取辨析对
    pairs = []

    # Pair 1: 王羲之 vs 王献之
    pairs.append({
        'id': 'pair_01_wangxizhi_vs_wangxianzhi',
        'file': 'card_01_王羲之vs王献之_中',
        'calligrapher_a': '王羲之',
        'style_tag_a': '雅正·含蓄·中和之美',
        'style_a': '书圣王羲之的草书代表了中国草书的最高境界。'
                    '特点：含蓄内敛，笔意连贯而不过度；结体秀美，骨力与柔情并存；'
                    '用笔精到，无一笔懈怠；整体气韵生动，风神潇洒。'
                    '线条含蓄不外露，连绵若有若无。',
        'calligrapher_b': '王献之',
        'style_tag_b': '外拓·奔放·创新精神',
        'style_b': '王献之是王羲之之子，书法与其父并称"二王"。'
                    '特点：外拓奔放，比其父更加放开；连绵草书更为显著；'
                    '笔势飞扬，个性强烈；结体开张，不拘一格。'
                    '线条外拓有锋芒，连绵大胆显著。',
        'character': '中',
        'character_script': '草书',
        'key_diff': '含蓄vs奔放 · 秀美vs开张 · 连绵节制vs大胆'
    })

    # Pair 2: 张旭 vs 怀素
    pairs.append({
        'id': 'pair_02_zhangxu_vs_huaisu',
        'file': 'card_02_张旭vs怀素_夫',
        'calligrapher_a': '张旭',
        'style_tag_a': '颠·圆·满纸云烟',
        'style_a': '张旭，世称"草圣"，与李白诗歌、裴旻剑舞并称"三绝"。'
                    '特点：线条粗细对比强烈，圆转如龙蛇；转折处以圆为主；'
                    '墨色浓淡对比鲜明；气势磅礴，满纸云烟；'
                    '笔势疾徐振荡，有"颠"之名。',
        'calligrapher_b': '怀素',
        'style_tag_b': '醉·瘦·骤雨旋风',
        'style_b': '怀素，与张旭并称"颠张醉素"。'
                    '特点：线条瘦硬如钢丝（与张旭显著区别）；'
                    '转折处锐角与圆转并存；墨色以枯为主（骤雨旋风形容其速度）；'
                    '字形大小悬殊，变化剧烈；连绵更甚，速度感更强。',
        'character': '夫',
        'character_script': '草书',
        'key_diff': '圆vs瘦 · 浓vs枯 · 磅礴vs迅疾'
    })

    # Pair 3: 孙过庭 vs 赵孟頫
    pairs.append({
        'id': 'pair_03_sunguoting_vs_zhaomengfu',
        'file': 'card_03_孙过庭vs赵孟頫_书',
        'calligrapher_a': '孙过庭',
        'style_tag_a': '今草·法度谨严·书谱之祖',
        'style_a': '孙过庭《书谱》是书法理论与实践的双重经典。'
                    '特点：严格遵循草法规范；字形相对独立（不完全连绵）；'
                    '笔法精到，学王羲之；墨色温润，气韵清雅。'
                    '线条古雅清劲，可识读性强。',
        'calligrapher_b': '赵孟頫',
        'style_tag_b': '复古·遒丽·圆润',
        'style_b': '赵孟頫提倡"复古"，书法各体皆精。'
                    '特点：楷行相融，以楷形行意；用笔遒丽圆润；'
                    '结体端正秀美；墨色华润。'
                    '线条秀美流畅，楷行相融但不过度连绵。',
        'character': '书',
        'character_script': '今草/行楷',
        'key_diff': '古雅vs圆润 · 法度vs秀美 · 草法规范vs行楷相融'
    })

    # Pair 4: 欧阳询 vs 颜真卿（楷书辨析）
    pairs.append({
        'id': 'pair_04_ouyangxun_vs_yanzhenqing',
        'file': 'card_04_欧阳询vs颜真卿_永',
        'calligrapher_a': '欧阳询',
        'style_tag_a': '险劲·瘦硬·法度森严',
        'style_a': '欧阳询，世称"楷书之圣"，与虞世南、褚遂良、柳公权并称初唐四大家。'
                    '特点：结体修长险劲（欧阳询典型特征）；笔画瘦硬；'
                    '法度森严，一丝不苟；结构精密，排列整齐。'
                    '整体风格刚健峻拔，险中求正。',
        'calligrapher_b': '颜真卿',
        'style_tag_b': '雄壮·浑厚·筋骨分明',
        'style_b': '颜真卿，唐代书法大家，楷书与欧阳询并称"颜柳欧赵"。'
                    '特点：结体方正宽博（与欧阳询修长形成鲜明对比）；笔画雄壮浑厚；'
                    '横细竖粗明显（颜体标志特征）；筋骨分明，气势恢宏。'
                    '整体风格刚健雄壮，饱满有力。',
        'character': '永',
        'character_script': '楷书',
        'key_diff': '修长vs宽博 · 瘦硬vs雄壮 · 险劲vs浑厚'
    })

    # Pair 5: 柳公权 vs 欧阳询（楷书辨析）
    pairs.append({
        'id': 'pair_05_liugongquan_vs_ouyangxun',
        'file': 'card_05_柳公权vs欧阳询_大',
        'calligrapher_a': '柳公权',
        'style_tag_a': '刚健·瘦硬·骨力洞达',
        'style_a': '柳公权，唐代书法家，与颜真卿并称"颜筋柳骨"。'
                    '特点：笔画刚健瘦硬（与颜真卿的"筋"相对）；'
                    '骨力洞达，力透纸背；结构严谨，法度分明。'
                    '整体风格清朗峻峭，以骨力见长。',
        'calligrapher_b': '欧阳询',
        'style_tag_b': '险劲·瘦硬·法度森严',
        'style_b': '欧阳询，隋唐之际书法巨匠，楷书之圣。'
                    '特点：结体修长险劲；笔画瘦硬精到；'
                    '法度森严，精密整齐；整体风格刚健峻拔。'
                    '结构精密险绝，险中求正。',
        'character': '大',
        'character_script': '楷书',
        'key_diff': '骨力vs险劲 · 瘦硬vs精密 · 柳骨vs欧险'
    })

    return pairs


def build_comparison_prompt(pair):
    """构建对比图 Prompt"""
    return (
        f"中国书法对比教学插图。\n"
        f"左侧：{pair['calligrapher_a']}，"
        f"{pair['style_tag_a']}，{pair['character_script']}。"
        f"风格特征：{pair['style_a']}\n"
        f"右侧：{pair['calligrapher_b']}，"
        f"{pair['style_tag_b']}，{pair['character_script']}。"
        f"风格特征：{pair['style_b']}\n"
        f"同一汉字「{pair['character']}」，{pair['character_script']}。"
        f"竖排左右两列布局，左侧书家名在左下方，右侧书家名在右下方。"
        f"底部中间标注辨析核心：{pair['key_diff']}。"
        f"教育教科书插图风格，纸张质感（米白色宣纸），"
        f"16:9宽屏构图，标注清晰，色彩区分左右两幅。"
    )


def build_single_artwork_prompt(pair):
    """构建单幅作品 Prompt（用于单独展示各书家）"""
    return (
        f"中国书法单幅作品展示。\n"
        f"书家：{pair['calligrapher_a']}，"
        f"{pair['style_tag_a']}，{pair['character_script']}。\n"
        f"风格特征：{pair['style_a']}\n"
        f"字：{pair['character']}，{pair['character_script']}。"
        f"画面居中大字，周围留白充足。"
        f"米白色宣纸质感，竖式构图。"
        f"右下角标注书家名和作品名。"
        f"教育教科书插图风格，高清，标注清晰。"
    )


def main():
    pairs = extract_pairs_from_ontology()
    prompts_dir = OUT_DIR / "prompts"
    prompts_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print(f"草书辨析卡 Prompt 提取")
    print(f"{'='*60}")

    for i, pair in enumerate(pairs, 1):
        comparison_prompt = build_comparison_prompt(pair)
        single_prompt = build_single_artwork_prompt(pair)

        # 保存对比 Prompt
        cmp_path = prompts_dir / f"{pair['file']}_对比图.txt"
        cmp_path.write_text(comparison_prompt, encoding='utf-8')

        # 保存单幅 Prompt
        sgl_path = prompts_dir / f"{pair['file']}_单幅.txt"
        sgl_path.write_text(single_prompt, encoding='utf-8')

        print(f"\n[{i}] {pair['file']}")
        print(f"    辨析：{pair['calligrapher_a']} vs {pair['calligrapher_b']} · {pair['character']}（{pair['character_script']}）")
        print(f"    核心差异：{pair['key_diff']}")
        print(f"    → {cmp_path.name}")
        print(f"    → {sgl_path.name}")

        # 打印 Prompt 摘要
        print(f"    [对比图 Prompt 摘要]")
        for line in comparison_prompt.split('\n'):
            if line.strip() and not line.startswith('    '):
                print(f"      {line.strip()[:80]}")

    print(f"\n{'='*60}")
    print(f"完成！共提取 {len(pairs)} 对辨析 Prompt")
    print(f"Prompt 文件目录：{prompts_dir}")
    print(f"{'='*60}\n")

    # 输出汇总 Markdown
    summary_path = prompts_dir / "_prompts_summary.md"
    lines = ["# 草书辨析卡 Prompt 汇总\n"]
    for i, pair in enumerate(pairs, 1):
        lines.append(f"## {i}. {pair['file']}")
        lines.append(f"**辨析对**：{pair['calligrapher_a']} vs {pair['calligrapher_b']}")
        lines.append(f"**字**：{pair['character']}（{pair['character_script']}）")
        lines.append(f"**核心差异**：{pair['key_diff']}")
        lines.append("")
        lines.append("```")
        lines.append(build_comparison_prompt(pair))
        lines.append("```")
        lines.append("")
    summary_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"汇总 Markdown：{summary_path}")


if __name__ == '__main__':
    main()
