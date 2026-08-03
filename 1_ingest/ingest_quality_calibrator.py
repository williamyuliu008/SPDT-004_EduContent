# -*- coding: utf-8 -*-
"""
1_ingest · ingest_quality_calibrator.py
=========================================
M2 阶段：双 Agent 质量校准

功能：
  1. Agent-A（提请方）：生成初稿知识条目
  2. Agent-B（质疑方）：对每条知识发起对抗质疑
  3. 仲裁层（Resolver）：判定接受/修正/拒绝
  4. 输出：ingested_entries + audit_log

用法：
  python ingest_quality_calibrator.py --input raw_entries.json --spec content_spec.yaml

依赖：
  pip install pyyaml jsonschema openai（或 deepseek API）
"""

import json
import argparse
import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, TypedDict
from dataclasses import dataclass, asdict, field
from enum import Enum

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ── 路径配置 ────────────────────────────────────────────────────────────────
SCHEMA_DIR = Path(__file__).parent / "schemas"
AUDIT_SCHEMA = SCHEMA_DIR / "audit_log.schema.json"
ENTRY_SCHEMA = SCHEMA_DIR / "ingested_entry.schema.json"
CONFIG_DIR = Path(__file__).parent / "config"

# ── API 配置 ────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_BASE = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com")


# ── 数据结构 ────────────────────────────────────────────────────────────────

class TrustLevel(Enum):
    C = "C"  # 大众来源
    D = "D"  # 编辑审核
    E = "E"  # 专家同行评审


class ChallengeType(Enum):
    FACT_ACCURACY = "fact_accuracy"           # 历史事实质疑
    DEFINITION_CONFLICT = "definition_conflict" # 概念定义质疑
    LOGIC_INCONSISTENCY = "logic_inconsistency" # 逻辑一致性质疑
    HALLUCINATION = "hallucination_detected"   # 幻觉检测


class Verdict(Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class Challenge:
    agent: str
    challenge_type: ChallengeType
    content: str
    verdict: Verdict
    resolution: str = ""


@dataclass
class CalibrationResult:
    ingested_id: str
    original_id: str
    concept: str
    definition: str
    trust: dict
    exam_tags: dict
    challenges: list[Challenge]
    rejected: bool
    output_status: str


@dataclass
class AuditLog:
    audit_id: str
    spec_id: str
    timestamp: str
    total_entries: int
    total_challenges: int
    accepted: int
    rejected: int
    rejected_reasons: dict
    trust_distribution: dict
    pass_rate: float
    pass_threshold: float
    overall_verdict: str


# ── LLM 调用 ────────────────────────────────────────────────────────────────

def call_llm(system_prompt: str, user_prompt: str, model: str = "deepseek-v4-flash") -> str:
    """调用 LLM API（DeepSeek / OpenAI 兼容）。"""
    if not API_KEY:
        print("[WARN] DEEPSEEK_API_KEY not set, using mock mode", file=sys.stderr)
        return mock_llm_response(user_prompt)

    import urllib.request

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.load(resp)
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[ERROR] LLM API call failed: {e}", file=sys.stderr)
        return ""


def mock_llm_response(prompt: str) -> str:
    """无 API Key 时的模拟响应（用于测试）。"""
    if "质疑" in prompt:
        return json.dumps([
            {"challenge_type": "fact_accuracy", "content": "该年份需要更精确确认"}
        ])
    elif "生成" in prompt:
        # 返回 dict（与真实 LLM 行为一致），而非数组
        return json.dumps({
            "concept": "模拟概念",
            "definition": "模拟定义内容（来自 mock LLM）",
            "structured_content": {"来源": "mock"},
            "trust": {"level": "C", "source": "mock_calibrator"},
            "exam_tags": {}
        })
    return "[]"


# ── Agent-A：提请方 ────────────────────────────────────────────────────────

AGENT_A_SYSTEM = """你是一个知识条目提请方（Agent-A）。
你的任务是根据原材料，生成结构化的知识条目（kb_vocab 格式）。
每条知识条目必须包含：concept / definition / structured_content / trust / exam_tags。
如果原材料中存在不确定信息，明确标注 [待考证]。"""


def agent_a_generate(raw_entry: dict, content_spec: dict) -> dict:
    """Agent-A：从原材料生成初稿知识条目。"""
    prompt = f"""原始材料：
{json.dumps(raw_entry, ensure_ascii=False, indent=2)}

考试大纲信息：
- 考试代码：{content_spec.get('spec_id', 'UNKNOWN')}
- 题型：{[qt['name'] for qt in content_spec.get('question_types', [])]}

请以 kb_vocab 格式生成知识条目。"""

    response = call_llm(AGENT_A_SYSTEM, prompt)
    try:
        # 尝试从响应中提取 JSON
        data = json.loads(response)
    except json.JSONDecodeError:
        # 降级：手工构造
        data = {
            "concept": raw_entry.get("concept", raw_entry.get("text", "未知")),
            "definition": raw_entry.get("definition", raw_entry.get("text", ""))[:300],
            "structured_content": {},
            "trust": {"level": "C", "source": "未校准"},
            "exam_tags": {}
        }
    return data


# ── Agent-B：质疑方 ────────────────────────────────────────────────────────

AGENT_B_SYSTEM = """你是一个知识条目质疑方（Agent-B）。
你的任务是对 Agent-A 生成的每条知识条目提出质疑。
质疑类型：
1. fact_accuracy：历史事实（年份/地点/人物关系）是否准确？
2. definition_conflict：概念定义是否符合学界共识？
3. logic_inconsistency：因果逻辑是否自洽？

对于每条条目，输出 JSON 格式的质疑列表：
[{{"challenge_type": "fact_accuracy|definition_conflict|logic_inconsistency", "content": "质疑内容"}}]

如果没有质疑，返回空列表 []。"""


def agent_b_challenge(entry: dict) -> list[dict]:
    """Agent-B：对知识条目提出质疑。"""
    prompt = f"""知识条目：
概念：{entry.get('concept', '')}
定义：{entry.get('definition', '')}
结构化内容：{json.dumps(entry.get('structured_content', {}), ensure_ascii=False)}

请提出质疑（JSON 格式）："""
    response = call_llm(AGENT_B_SYSTEM, prompt)
    try:
        challenges = json.loads(response)
        return challenges if isinstance(challenges, list) else []
    except json.JSONDecodeError:
        return []


# ── Resolver：仲裁层 ─────────────────────────────────────────────────────

def resolve_challenges(challenges: list[dict], original_entry: dict) -> tuple[list[Challenge], bool]:
    """
    仲裁层判定。
    规则：
    - hallucination_detected → 直接拒绝
    - 3个以上不同类型质疑 → 拒绝
    - 1-2个质疑 → 修正（保留概念，修正定义）
    - 0个质疑 → 接受
    """
    if not challenges:
        return [], False

    resolved = []
    for ch in challenges:
        ct = ChallengeType(ch.get("challenge_type", "fact_accuracy"))
        if ct == ChallengeType.HALLUCINATION:
            resolved.append(Challenge(
                agent="Resolver",
                challenge_type=ct,
                content=ch.get("content", ""),
                verdict=Verdict.REJECTED,
                resolution="幻觉检测触发，直接拒绝"
            ))
            return resolved, True

    type_set = set(ch.get("challenge_type") for ch in challenges)
    if len(type_set) >= 3:
        resolved.append(Challenge(
            agent="Resolver",
            challenge_type=ChallengeType.LOGIC_INCONSISTENCY,
            content=f"发现{len(type_set)}种不同类型质疑，整体不可靠",
            verdict=Verdict.REJECTED,
            resolution="多类型质疑，拒绝"
        ))
        return resolved, True

    for ch in challenges:
        ct = ChallengeType(ch.get("challenge_type", "fact_accuracy"))
        resolved.append(Challenge(
            agent="Resolver",
            challenge_type=ct,
            content=ch.get("content", ""),
            verdict=Verdict.MODIFIED,
            resolution=f"接受质疑：{ch.get('content', '')[:50]}"
        ))
    return resolved, False


# ── 主校准流程 ────────────────────────────────────────────────────────────

def calibrate(
    raw_entries: list[dict],
    content_spec: dict,
    spec_id: str = "UNKNOWN"
) -> tuple[list[CalibrationResult], AuditLog]:
    """双 Agent 质量校准主流程。"""

    results: list[CalibrationResult] = []
    all_challenges: list[dict] = []
    rejected_count = 0
    trust_dist = {"E": 0, "D": 0, "C": 0}
    reason_dist = {"fact_inaccuracy": 0, "definition_conflict": 0, "hallucination_detected": 0, "logic_inconsistency": 0}

    for i, raw in enumerate(raw_entries):
        raw_id = raw.get("id", raw.get("raw_id", f"RAW_{i+1:03d}"))

        # Agent-A 生成
        draft = agent_a_generate(raw, content_spec)
        concept = draft.get("concept", "")
        definition = draft.get("definition", "")[:300]
        trust_lvl = draft.get("trust", {}).get("level", "C")

        # Agent-B 质疑
        challenges_raw = agent_b_challenge(draft)
        challenges, was_rejected = resolve_challenges(challenges_raw, draft)
        all_challenges.extend([
            {"entry_id": raw_id, **ch} for ch in challenges_raw
        ])

        if was_rejected:
            rejected_count += 1
            results.append(CalibrationResult(
                ingested_id=f"REJ_{spec_id}_{i+1:03d}",
                original_id=raw_id,
                concept=concept,
                definition=definition,
                trust={"level": trust_lvl, "source": "rejected"},
                exam_tags={},
                challenges=challenges,
                rejected=True,
                output_status="rejected"
            ))
            continue

        # 可信度统计
        trust_dist[trust_lvl] = trust_dist.get(trust_lvl, 0) + 1

        results.append(CalibrationResult(
            ingested_id=f"ING_{spec_id}_{i+1:03d}",
            original_id=raw_id,
            concept=concept,
            definition=definition,
            trust=draft.get("trust", {}),
            exam_tags=draft.get("exam_tags", {}),
            challenges=challenges,
            rejected=False,
            output_status="ready_for_2_structure"
        ))

    total = len(raw_entries)
    pass_count = total - rejected_count
    pass_rate = pass_count / total if total > 0 else 0.0

    audit = AuditLog(
        audit_id=f"AUDIT_{spec_id}_{datetime.now().strftime('%Y%m%d')}_{len(raw_entries):03d}",
        spec_id=spec_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_entries=total,
        total_challenges=len(all_challenges),
        accepted=pass_count,
        rejected=rejected_count,
        rejected_reasons=reason_dist,
        trust_distribution=trust_dist,
        pass_rate=round(pass_rate, 3),
        pass_threshold=0.80,
        overall_verdict="PASS" if pass_rate >= 0.80 else "FAIL"
    )

    return results, audit


# ── 输出序列化 ─────────────────────────────────────────────────────────────

def serialize_result(r: CalibrationResult) -> dict:
    return {
        "ingested_id": r.ingested_id,
        "source_raw_id": r.original_id,
        "concept": r.concept,
        "definition": r.definition,
        "structured_content": r.challenges[0].resolution if r.challenges else {},
        "trust": r.trust,
        "exam_tags": r.exam_tags,
        "calibration": {
            "challenges": [
                {
                    "agent": ch.agent,
                    "challenge_type": ch.challenge_type.value,
                    "content": ch.content,
                    "verdict": ch.verdict.value,
                    "resolution": ch.resolution
                }
                for ch in r.challenges
            ],
            "rejected_entries": []
        },
        "output_status": r.output_status
    }


def main():
    parser = argparse.ArgumentParser(
        description="1_ingest · M2 双Agent质量校准"
    )
    parser.add_argument("--input", "-i", required=True, help="原材料 JSON 文件")
    parser.add_argument("--spec", "-s", required=True, help="ContentSpec YAML 文件")
    parser.add_argument("--output-dir", "-o", default=None, help="输出目录")
    parser.add_argument("--mock", action="store_true", help="使用模拟 LLM 响应")

    args = parser.parse_args()

    input_path = Path(args.input)
    spec_path = Path(args.spec)
    output_dir = Path(args.output_dir) if args.output_dir else input_path.parent

    # 加载原材料
    with open(input_path, encoding="utf-8") as f:
        raw_entries = json.load(f)
    if isinstance(raw_entries, dict) and "entries" in raw_entries:
        raw_entries = raw_entries["entries"]

    # 加载 ContentSpec
    with open(spec_path, encoding="utf-8") as f:
        content_spec = yaml.safe_load(f) if HAS_YAML else json.load(f)

    spec_id = content_spec.get("spec_id", input_path.stem)

    # 校准
    print(f"[INFO] Starting calibration: {len(raw_entries)} entries")
    results, audit = calibrate(raw_entries, content_spec, spec_id)

    # 写入输出
    output_dir.mkdir(parents=True, exist_ok=True)
    ingested_path = output_dir / f"{spec_id}_ingested.json"
    audit_path = output_dir / f"{spec_id}_audit.json"

    with open(ingested_path, "w", encoding="utf-8") as f:
        json.dump(
            [serialize_result(r) for r in results],
            f, ensure_ascii=False, indent=2
        )

    with open(audit_path, "w", encoding="utf-8") as f:
        json.dump(asdict(audit), f, ensure_ascii=False, indent=2)

    print(f"\n[校准完成]")
    print(f"  总条目：    {audit.total_entries}")
    print(f"  通过：      {audit.accepted}")
    print(f"  拒绝：      {audit.rejected}")
    print(f"  通过率：    {audit.pass_rate:.1%}")
    print(f"  判定：      {audit.overall_verdict}")
    print(f"  可信度分布：E={audit.trust_distribution['E']} D={audit.trust_distribution['D']} C={audit.trust_distribution['C']}")
    print(f"\n  输出：{ingested_path}")
    print(f"  日志：{audit_path}")


if __name__ == "__main__":
    main()
