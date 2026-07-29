"""
高考志愿填报模块 - 智能推荐引擎
核心算法：批次定位 + 院校筛选 + 概率计算 + 志愿推荐
"""

from typing import Optional
from dataclasses import dataclass
import json
from datetime import datetime

from data_model import (
    University, Major, AdmissionScore, BatchLine,
    VolunteerStrategy, UserProfile, MatchResult,
    VolunteerPlan, MatchTier, RiskLevel, RiskTolerance,
    StrategyPrinciple, SAMPLE_UNIVERSITIES, SAMPLE_MAJORS,
    SAMPLE_SCORES, SAMPLE_BATCH_LINES
)


@dataclass
class MatchConfig:
    """推荐引擎配置"""
    # 分数级差配置
    chase_threshold: int = 0        # 冲: 0 ~ -5
    secure_threshold: int = -15      # 稳: -5 ~ -15
    safe_threshold: int = -30        # 保: -15 ~ -30
    buffer_threshold: int = -999     # 垫: < -30
    
    # 每档志愿数量
    chase_min: int = 3
    chase_max: int = 5
    secure_min: int = 3
    secure_max: int = 5
    safe_min: int = 3
    safe_max: int = 5
    buffer_min: int = 2
    buffer_max: int = 3
    
    # 概率计算配置
    probability_thresholds = {
        "稳妥": 0.85,
        "中等": 0.60,
        "激进": 0.30,
        "高风险": 0.0
    }


class MatchingEngine:
    """
    志愿推荐引擎
    
    核心功能：
    1. 批次定位 - 根据分数确定可报考批次
    2. 院校筛选 - 按偏好过滤院校池
    3. 概率计算 - 基于历史数据评估录取概率
    4. 智能推荐 - 生成冲稳安保方案
    """
    
    def __init__(
        self,
        universities: list[University] = None,
        majors: list[Major] = None,
        scores: list[AdmissionScore] = None,
        batch_lines: list[BatchLine] = None,
        config: MatchConfig = None
    ):
        # 数据存储
        self.universities = universities or SAMPLE_UNIVERSITIES
        self.majors = majors or SAMPLE_MAJORS
        self.scores = scores or SAMPLE_SCORES
        self.batch_lines = batch_lines or SAMPLE_BATCH_LINES
        self.config = config or MatchConfig()
        
        # 建立索引
        self._build_indexes()
    
    def _build_indexes(self):
        """建立数据索引，加速查询"""
        # 院校索引: code -> University
        self.university_index = {u.code: u for u in self.universities}
        
        # 专业索引: code -> Major
        self.major_index = {m.code: m for m in self.majors}
        
        # 分数索引: (year, province, university_code, major_code) -> [scores]
        self.score_index = {}
        for s in self.scores:
            key = (s.year, s.province, s.university_code, s.major_code or "")
            if key not in self.score_index:
                self.score_index[key] = []
            self.score_index[key].append(s)
        
        # 批次线索引: (year, province, batch) -> BatchLine
        self.batch_line_index = {
            (bl.year, bl.province, bl.batch): bl
            for bl in self.batch_lines
        }
    
    def locate_batch(self, user: UserProfile) -> dict:
        """
        Step 1: 批次定位
        
        根据用户分数和省份，确定可报考的批次
        返回：批次信息 + 分差分析
        """
        # 获取最新年份的批次线
        year = max(bl.year for bl in self.batch_lines)
        
        results = []
        for batch_line in self.batch_lines:
            if batch_line.year == year and batch_line.province == user.province:
                diff = user.score - batch_line.score_line
                results.append({
                    "batch": batch_line.batch,
                    "line": batch_line.score_line,
                    "rank_line": batch_line.rank_line,
                    "difference": diff,
                    "over_line_pct": (diff / batch_line.score_line) * 100 if diff > 0 else 0,
                    "status": self._get_batch_status(diff, batch_line.batch)
                })
        
        # 按批次优先级排序
        batch_order = {"本科一批": 1, "本科二批": 2, "专科提前批": 3, "专科批": 4}
        results.sort(key=lambda x: batch_order.get(x["batch"], 99))
        
        return {
            "user_score": user.score,
            "user_rank": user.rank,
            "province": user.province,
            "year": year,
            "batches": results
        }
    
    def _get_batch_status(self, diff: int, batch: str) -> str:
        """获取批次状态描述"""
        if diff < 0:
            return f"未达{batch}线"
        elif diff <= 5:
            return f"踩{batch}线"
        elif diff <= 20:
            return f"超{batch}线{diff}分"
        else:
            return f"大幅超{batch}线{diff}分"
    
    def filter_universities(
        self,
        user: UserProfile,
        strategy: VolunteerStrategy,
        target_batch: str = "本科批"
    ) -> list[University]:
        """
        Step 2: 院校筛选
        
        根据用户偏好和批次要求，筛选候选院校
        """
        candidates = []
        
        for uni in self.universities:
            # 检查省份偏好
            if strategy.preferred_provinces:
                if uni.province not in strategy.preferred_provinces:
                    # 除非是排除省份
                    if uni.province not in strategy.exclude_provinces:
                        continue  # 不在偏好省份，跳过
            
            # 检查排除省份
            if uni.province in strategy.exclude_provinces:
                continue
            
            # 检查等级偏好
            if strategy.preferred_levels:
                has_preferred = any(
                    level in uni.level 
                    for level in strategy.preferred_levels
                )
                if not has_preferred:
                    continue
            
            candidates.append(uni)
        
        return candidates
    
    def calculate_probability(
        self,
        user: UserProfile,
        score_record: AdmissionScore,
        config: MatchConfig = None
    ) -> tuple[float, RiskLevel]:
        """
        Step 3: 计算录取概率
        
        基于分差计算录取概率和风险等级
        
        规则：
        - 分差 >= 5: 稳妥 (95%)
        - 分差 >= 0: 中等 (80%)
        - 分差 >= -10: 中等偏激进 (60%)
        - 分差 >= -20: 激进 (40%)
        - 分差 < -20: 高风险 (20%)
        """
        config = config or self.config
        diff = user.score - score_record.score_min
        
        if diff >= 5:
            return 0.95, RiskLevel.SAFE
        elif diff >= 0:
            return 0.80, RiskLevel.MEDIUM
        elif diff >= -10:
            return 0.60, RiskLevel.MEDIUM
        elif diff >= -20:
            return 0.40, RiskLevel.RISKY
        else:
            return 0.20, RiskLevel.HIGH_RISK
    
    def determine_tier(
        self,
        score_difference: int,
        config: MatchConfig = None
    ) -> MatchTier:
        """
        确定志愿档次（冲稳安保）
        """
        config = config or self.config
        
        if score_difference >= config.chase_threshold:
            return MatchTier.CHASE
        elif score_difference >= config.secure_threshold:
            return MatchTier.SECURE
        elif score_difference >= config.safe_threshold:
            return MatchTier.SAFE
        else:
            return MatchTier.BUFFER
    
    def generate_recommendations(
        self,
        user: UserProfile,
        strategy: VolunteerStrategy,
        config: MatchConfig = None
    ) -> VolunteerPlan:
        """
        Step 4 & 5: 生成推荐方案
        
        核心算法：
        1. 定位批次
        2. 筛选院校池
        3. 计算每个院校的录取概率
        4. 按策略排序
        5. 生成分数级差结构
        """
        config = config or self.config
        
        # Step 1: 批次定位
        batch_info = self.locate_batch(user)
        if not batch_info["batches"]:
            return self._empty_plan(user, strategy, "无可用批次数据")
        
        target_batch = batch_info["batches"][0]["batch"]
        
        # Step 2: 筛选院校
        candidates = self.filter_universities(user, strategy, target_batch)
        
        # Step 3: 收集分数数据并计算概率
        match_results: list[MatchResult] = []
        
        for uni in candidates:
            # 获取该院校的最新分数
            score_key = (2025, user.province, uni.code, "")
            score_records = self.score_index.get(score_key, [])
            
            if not score_records:
                continue
            
            score_record = score_records[0]  # 取第一条记录
            
            # 检查是否过批次线
            if not score_record.is_above_line(user.score):
                continue
            
            # 计算概率
            probability, risk_level = self.calculate_probability(user, score_record, config)
            score_diff = user.score - score_record.score_min
            tier = self.determine_tier(score_diff, config)
            
            # 生成推荐理由
            reason = self._generate_reason(user, uni, score_diff, risk_level)
            
            result = MatchResult(
                university=uni,
                major=None,
                admission_score=score_record,
                probability=probability,
                risk_level=risk_level,
                score_difference=score_diff,
                tier=tier,
                reason=reason
            )
            match_results.append(result)
        
        # Step 4: 按策略排序
        sorted_results = self._sort_by_strategy(match_results, strategy)
        
        # Step 5: 生成分数级差
        tiered_results = self._distribute_to_tiers(sorted_results, config)
        
        # 构建方案
        plan = VolunteerPlan(
            user_profile=user,
            strategy=strategy,
            tier_results=tiered_results,
            total_volunteers=sum(len(v) for v in tiered_results.values()),
            create_time=datetime.now().isoformat()
        )
        
        return plan
    
    def _sort_by_strategy(
        self,
        results: list[MatchResult],
        strategy: VolunteerStrategy
    ) -> list[MatchResult]:
        """按策略原则排序"""
        
        if strategy.principle == StrategyPrinciple.SCORE_FIRST:
            # 分数优先：按分差降序（分差越大越好）
            return sorted(
                results,
                key=lambda x: (-x.score_difference, x.university.rank_national)
            )
        
        elif strategy.principle == StrategyPrinciple.UNIVERSITY_FIRST:
            # 院校优先：按院校排名升序
            return sorted(
                results,
                key=lambda x: (x.university.rank_national, -x.score_difference)
            )
        
        elif strategy.principle == StrategyPrinciple.MAJOR_FIRST:
            # 专业优先：暂按专业排名（需要major数据支持）
            return sorted(
                results,
                key=lambda x: (-x.score_difference, x.university.rank_national)
            )
        
        return results
    
    def _distribute_to_tiers(
        self,
        sorted_results: list[MatchResult],
        config: MatchConfig
    ) -> dict[MatchTier, list[MatchResult]]:
        """将排序结果分配到各档次"""
        
        tiered: dict[MatchTier, list[MatchResult]] = {
            MatchTier.CHASE: [],
            MatchTier.SECURE: [],
            MatchTier.SAFE: [],
            MatchTier.BUFFER: []
        }
        
        for result in sorted_results:
            tier = result.tier
            tier_list = tiered[tier]
            
            # 检查是否超过该档次的最大数量
            max_count = getattr(config, f"{tier.value}_max", 5)
            if len(tier_list) < max_count:
                tier_list.append(result)
        
        # 确保每档至少有一定数量
        self._balance_tiers(tiered, config)
        
        return tiered
    
    def _balance_tiers(
        self,
        tiered: dict[MatchTier, list[MatchResult]],
        config: MatchConfig
    ):
        """平衡各档次的志愿数量"""
        
        # 收集所有结果
        all_results = []
        for tier in [MatchTier.CHASE, MatchTier.SECURE, MatchTier.SAFE, MatchTier.BUFFER]:
            all_results.extend([(r, tier) for r in tiered[tier]])
        
        # 按分差降序
        all_results.sort(key=lambda x: x[0].score_difference, reverse=True)
        
        # 重新分配
        for tier in tiered:
            tiered[tier] = []
        
        for result, _ in all_results:
            # 确定应该属于哪个档次
            tier = result.tier
            tier_list = tiered[tier]
            
            # 检查是否需要调整（防止某些档次太空）
            if len(tiered[tier]) >= getattr(config, f"{tier.value}_max", 5):
                # 找最接近的档次
                for alt_tier in [MatchTier.SECURE, MatchTier.SAFE, MatchTier.BUFFER]:
                    if len(tiered[alt_tier]) < getattr(config, f"{alt_tier.value}_max", 5):
                        tier = alt_tier
                        tier_list = tiered[tier]
                        break
            
            if len(tier_list) < getattr(config, f"{tier.value}_max", 5):
                tier_list.append(result)
    
    def _generate_reason(
        self,
        user: UserProfile,
        university: University,
        score_diff: int,
        risk_level: RiskLevel
    ) -> str:
        """生成推荐理由"""
        reasons = []
        
        # 等级标签
        if "985" in university.level:
            reasons.append("985工程院校")
        elif "211" in university.level:
            reasons.append("211工程院校")
        elif "双一流" in university.level:
            reasons.append("双一流建设高校")
        
        # 排名信息
        reasons.append(f"全国排名{university.rank_national}")
        
        # 分差信息
        if score_diff >= 5:
            reasons.append("录取概率较高")
        elif score_diff >= 0:
            reasons.append("有一定录取把握")
        else:
            reasons.append("存在一定风险，但值得冲刺")
        
        return "，".join(reasons)
    
    def _empty_plan(
        self,
        user: UserProfile,
        strategy: VolunteerStrategy,
        message: str
    ) -> VolunteerPlan:
        """生成空方案"""
        return VolunteerPlan(
            user_profile=user,
            strategy=strategy,
            tier_results={},
            total_volunteers=0,
            create_time=datetime.now().isoformat()
        )
    
    def get_university_by_code(self, code: str) -> Optional[University]:
        """根据代码获取院校"""
        return self.university_index.get(code)
    
    def get_major_by_code(self, code: str) -> Optional[Major]:
        """根据代码获取专业"""
        return self.major_index.get(code)
    
    def get_scores_for_university(
        self,
        university_code: str,
        year: int = 2025,
        province: str = "上海"
    ) -> list[AdmissionScore]:
        """获取院校的分数数据"""
        # 院校投档线
        key = (year, province, university_code, "")
        results = self.score_index.get(key, [])
        
        # 专业分数
        for major in self.majors:
            key = (year, province, university_code, major.code)
            results.extend(self.score_index.get(key, []))
        
        return results


def demo():
    """演示推荐引擎"""
    
    print("=" * 60)
    print("高考志愿填报 - 智能推荐引擎演示")
    print("=" * 60)
    
    # 创建引擎实例
    engine = MatchingEngine()
    
    # 创建用户档案（假设上海考生，600分）
    user = UserProfile(
        province="上海",
        score=600,
        rank=500,
        subjects=["物理", "化学", "生物"]
    )
    
    # 创建策略
    strategy = VolunteerStrategy.default_strategy()
    strategy.preferred_provinces = ["上海", "北京", "江苏"]
    strategy.preferred_levels = ["985", "211", "双一流"]
    
    print(f"\n【用户信息】")
    print(f"  省份: {user.province}")
    print(f"  分数: {user.score}分")
    print(f"  排名: {user.rank}名")
    print(f"  选科: {', '.join(user.subjects)}")
    
    print(f"\n【策略偏好】")
    print(f"  优先原则: {strategy.principle.value}")
    print(f"  风险偏好: {strategy.risk_tolerance.value}")
    print(f"  偏好省份: {', '.join(strategy.preferred_provinces) or '不限'}")
    print(f"  偏好等级: {', '.join(strategy.preferred_levels)}")
    
    # 批次定位
    print(f"\n【批次定位】")
    batch_info = engine.locate_batch(user)
    for batch in batch_info["batches"]:
        print(f"  {batch['batch']}: {batch['line']}分 (超{batch['difference']}分) - {batch['status']}")
    
    # 生成推荐
    print(f"\n【智能推荐】")
    plan = engine.generate_recommendations(user, strategy)
    
    for tier in [MatchTier.CHASE, MatchTier.SECURE, MatchTier.SAFE, MatchTier.BUFFER]:
        results = plan.tier_results.get(tier, [])
        if results:
            print(f"\n  [{tier.value}档] ({len(results)}个志愿)")
            for i, r in enumerate(results, 1):
                uni = r.university
                print(f"    {i}. {uni.name} ({uni.code})")
                print(f"       等级: {uni.get_display_level()} | 全国排名: {uni.rank_national}")
                print(f"       历史最低分: {r.admission_score.score_min} | 分差: {r.score_difference:+d}")
                print(f"       概率: {r.get_probability_display()} | 风险: {r.get_risk_display()}")
                print(f"       理由: {r.reason}")
    
    print(f"\n【方案统计】")
    print(f"  总志愿数: {plan.total_volunteers}")
    print(f"  生成时间: {plan.create_time}")
    print(f"  方案有效: {'是' if plan.is_valid() else '否'}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()
