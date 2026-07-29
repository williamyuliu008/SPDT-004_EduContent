"""
高考志愿填报模块 - 数据模型
定义院校、专业、分数、策略等核心数据结构
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ============== 枚举定义 ==============

class UniversityLevel(str, Enum):
    """院校等级"""
    C9 = "C9"           # 清华、北大、复旦、上交、南大、浙大、中科大、哈工大、西交
    NINE_FIVE = "985"    # 985工程
    TWO_ONE_ONE = "211"  # 211工程
    DOUBLE_FIRST = "双一流"  # 双一流建设
    ORDINARY = "普通"    # 普通本科


class UniversityType(str, Enum):
    """院校类型"""
    COMPREHENSIVE = "综合"    # 综合类
    SCIENCE_ENGINEERING = "理工"  # 理工类
    NORMAL = "师范"        # 师范类
    MEDICINE = "医药"      # 医药类
    AGRICULTURE = "农业"    # 农业类
    ECONOMICS = "财经"     # 财经类
    LAW = "政法"          # 政法类
    ARTS = "艺术"         # 艺术类
    LANGUAGE = "语言"      # 语言类
    MILITARY = "军事"      # 军事类


class Batch(str, Enum):
    """录取批次"""
    PRIORITY_FIRST = "本科一批"   # 重点本科
    PRIORITY_SECOND = "本科二批"  # 普通本科
    JUNIOR_FIRST = "专科提前批"
    JUNIOR_NORMAL = "专科批"


class DegreeType(str, Enum):
    """学位类型"""
    SCIENCE = "理学"    # 理学学士
    ENGINEERING = "工学"  # 工学学士
    ARTS = "艺术学"    # 艺术学学士
    LITERATURE = "文学"  # 文学学士
    MANAGEMENT = "管理学"  # 管理学学士
    ECONOMICS = "经济学"  # 经济学学士
    LAW = "法学"       # 法学学士
    EDUCATION = "教育学"  # 教育学学士


class StrategyPrinciple(str, Enum):
    """志愿填报策略原则"""
    SCORE_FIRST = "分数优先"    # 最大化院校层次
    UNIVERSITY_FIRST = "院校优先"  # 确保目标院校
    MAJOR_FIRST = "专业优先"    # 锁定目标专业


class RiskTolerance(str, Enum):
    """风险偏好"""
    CONSERVATIVE = "保守"  # 稳妥为主
    MODERATE = "稳健"     # 稳中求进
    AGGRESSIVE = "激进"   # 敢于冲刺


class RiskLevel(str, Enum):
    """风险等级"""
    SAFE = "稳妥"      # >85% 录取概率
    MEDIUM = "中等"     # 60-85%
    RISKY = "激进"     # 30-60%
    HIGH_RISK = "高风险"  # <30%


class MatchTier(str, Enum):
    """志愿档次（冲稳安保）"""
    CHASE = "冲"    # 冲刺批次
    SECURE = "稳"   # 稳妥批次
    SAFE = "保"     # 保底批次
    BUFFER = "垫"   # 垫底批次


# ============== 核心数据模型 ==============

@dataclass
class University:
    """
    院校实体
    """
    code: str                          # 院校代码，如 "10001"
    name: str                           # 院校名称
    province: str                       # 所在省份
    city: str                           # 所在城市
    level: list[str]                    # 等级标签，如 ["985", "211", "双一流"]
    type: str                           # 院校类型：综合/理工/师范/...
    rank_national: int                  # 全国排名
    rank_subject: dict[str, int] = field(default_factory=dict)  # 分专业排名
    website: str = ""
    enrollment_count: int = 0           # 招生人数
    tuition_avg: int = 0                # 平均学费（元/年）
    description: str = ""               # 院校简介
    
    def has_level(self, target_level: str) -> bool:
        """检查是否具有特定等级"""
        return target_level in self.level
    
    def get_display_level(self) -> str:
        """获取等级显示文本"""
        return "+".join(self.level) if self.level else "普通"


@dataclass
class Major:
    """
    专业实体
    """
    code: str                           # 专业代码，如 "080501"
    name: str                           # 专业名称
    category: str                       # 专业类别：计算机/电子/机械/...
    degree: str                         # 学位类型：理学/工学/管理学/...
    duration_years: int = 4            # 学制（年）
    is_enrollment: bool = True          # 是否在目标省份招生
    subject_evaluation: str = ""        # 学科评估等级：A+/A/B+...
    employment_rate: float = 0.0        # 就业率
    avg_salary: int = 0                 # 平均月薪（元）
    description: str = ""               # 专业简介
    
    def get_category_display(self) -> str:
        """获取专业类别显示"""
        category_map = {
            "计算机": "计算机类",
            "电子": "电子信息类",
            "机械": "机械类",
            "土木": "土木类",
            "经济": "经济类",
            "管理": "管理类",
            "文学": "文学类",
            "法学": "法学类",
            "医学": "医学类",
        }
        return category_map.get(self.category, self.category)


@dataclass
class AdmissionScore:
    """
    录取分数记录
    """
    year: int                           # 年份：2023/2024/2025
    province: str                       # 省份
    university_code: str                # 院校代码
    major_code: str                    # 专业代码（空字符串表示院校投档线）
    major_name: str = ""                # 专业名称（方便显示）
    score_min: int                      # 最低分（投档线/专业线）
    score_avg: int                      # 平均分
    rank: int                           # 省排名
    batch: str                          # 批次：本科一批/本科二批/专科批
    enrollment_count: int = 0          # 招生人数
    highest_score: int = 0              # 最高分
    
    def get_score_difference(self, user_score: int) -> int:
        """计算与用户分数的分差"""
        return user_score - self.score_min
    
    def is_above_line(self, user_score: int) -> bool:
        """判断是否过线"""
        return user_score >= self.score_min


@dataclass
class BatchLine:
    """
    批次控制线
    """
    year: int                           # 年份
    province: str                       # 省份
    batch: str                          # 批次
    score_line: int                     # 批次线分数
    rank_line: int                      # 对应排名
    

@dataclass
class VolunteerStrategy:
    """
    用户志愿填报策略
    """
    principle: StrategyPrinciple        # 优先策略
    risk_tolerance: RiskTolerance       # 风险偏好
    preferred_provinces: list[str] = field(default_factory=list)  # 偏好省份
    preferred_levels: list[str] = field(default_factory=list)     # 偏好院校等级
    preferred_categories: list[str] = field(default_factory=list) # 偏好专业类别
    exclude_provinces: list[str] = field(default_factory=list)    # 排除省份
    avoid调剂: bool = True              # 是否接受调剂
    
    @classmethod
    def default_strategy(cls) -> "VolunteerStrategy":
        """创建默认策略"""
        return cls(
            principle=StrategyPrinciple.SCORE_FIRST,
            risk_tolerance=RiskTolerance.MODERATE,
            preferred_provinces=[],
            preferred_levels=["985", "211", "双一流"],
            preferred_categories=[],
            exclude_provinces=[],
            avoid调剂=False
        )


@dataclass
class MatchResult:
    """
    志愿匹配结果
    """
    university: University              # 目标院校
    major: Optional[Major]              # 目标专业（可为None表示大类招生）
    admission_score: AdmissionScore    # 历史录取分数
    probability: float                  # 录取概率估算（0-1）
    risk_level: RiskLevel              # 风险等级
    score_difference: int              # 与用户分数的分差
    tier: MatchTier                    # 志愿档次（冲稳安保）
    reason: str = ""                   # 推荐理由
    alternative_majors: list[Major] = field(default_factory=list)  # 备选专业
    
    def get_probability_display(self) -> str:
        """获取概率显示文本"""
        return f"{self.probability * 100:.0f}%"
    
    def get_risk_display(self) -> str:
        """获取风险显示"""
        return self.risk_level.value
    
    def get_tier_display(self) -> str:
        """获取档次显示"""
        return self.tier.value


@dataclass
class UserProfile:
    """
    用户档案
    """
    province: str                       # 高考省份
    score: int                          # 高考分数
    rank: int                           # 省排名
    subjects: list[str] = field(default_factory=list)  # 选考科目
    preferred_batch: str = ""           # 目标批次
    
    def __post_init__(self):
        if not self.subjects:
            self.subjects = ["语文", "数学", "外语"]  # 传统文/理综


@dataclass  
class VolunteerPlan:
    """
    完整志愿方案
    """
    user_profile: UserProfile           # 用户信息
    strategy: VolunteerStrategy         # 填报策略
    tier_results: dict[MatchTier, list[MatchResult]] = field(default_factory=dict)
    total_volunteers: int = 0           # 总志愿数
    create_time: str = ""               # 创建时间
    version: str = "1.0"                # 方案版本
    
    def get_tier_count(self, tier: MatchTier) -> int:
        """获取指定档次的志愿数量"""
        return len(self.tier_results.get(tier, []))
    
    def get_total_count(self) -> int:
        """获取总志愿数"""
        return sum(len(v) for v in self.tier_results.values())
    
    def is_valid(self) -> bool:
        """检查方案是否有效"""
        total = self.get_total_count()
        return 6 <= total <= 30  # 合理志愿数量范围


# ============== 数据示例（真实院校数据）==============

SAMPLE_UNIVERSITIES = [
    University(
        code="10001",
        name="北京大学",
        province="北京",
        city="北京市",
        level=["985", "211", "双一流", "C9"],
        type="综合",
        rank_national=1,
        rank_subject={"计算机": 1, "数学": 1, "物理学": 1, "中国语言文学": 1, "经济学": 1},
        website="https://www.pku.edu.cn",
        enrollment_count=4000,
        tuition_avg=5000,
        description="中国最顶尖的综合性大学，国家重点建设的世界一流大学。"
    ),
    University(
        code="10003",
        name="清华大学",
        province="北京",
        city="北京市",
        level=["985", "211", "双一流", "C9"],
        type="理工",
        rank_national=2,
        rank_subject={"计算机": 2, "电子信息": 1, "机械工程": 1, "建筑学": 1, "材料科学": 1},
        website="https://www.tsinghua.edu.cn",
        enrollment_count=3800,
        tuition_avg=5000,
        description="中国最顶尖的理工类大学，被誉为'红色工程师的摇篮'。"
    ),
    University(
        code="10247",
        name="同济大学",
        province="上海",
        city="上海市",
        level=["985", "211", "双一流"],
        type="理工",
        rank_national=15,
        rank_subject={"土木工程": 1, "建筑学": 2, "城乡规划": 1, "环境工程": 3, "交通运输": 2},
        website="https://www.tongji.edu.cn",
        enrollment_count=4500,
        tuition_avg=6500,
        description="以土木工程闻名的综合性大学，建筑类专业全国领先。"
    ),
    University(
        code="10246",
        name="复旦大学",
        province="上海",
        city="上海市",
        level=["985", "211", "双一流", "C9"],
        type="综合",
        rank_national=5,
        rank_subject={"新闻传播": 1, "中国语言文学": 2, "哲学": 1, "经济学": 3, "管理学": 3},
        website="https://www.fudan.edu.cn",
        enrollment_count=3500,
        tuition_avg=5500,
        description="人文社科见长的综合性大学，新闻传播和哲学专业全国第一。"
    ),
    University(
        code="10248",
        name="上海交通大学",
        province="上海",
        city="上海市",
        level=["985", "211", "双一流", "C9"],
        type="理工",
        rank_national=4,
        rank_subject={"机械工程": 2, "船舶与海洋": 1, "电子信息": 2, "计算机": 3, "管理学": 2},
        website="https://www.sjtu.edu.cn",
        enrollment_count=4200,
        tuition_avg=5000,
        description="工科强校，船舶与海洋工程连续多年全国第一。"
    ),
]

SAMPLE_MAJORS = [
    Major(
        code="080501",
        name="计算机科学与技术",
        category="计算机",
        degree="工学",
        duration_years=4,
        is_enrollment=True,
        subject_evaluation="A+",
        employment_rate=0.95,
        avg_salary=15000,
        description="培养计算机系统、软件工程、人工智能等领域的高级专门人才。"
    ),
    Major(
        code="080701",
        name="电子信息工程",
        category="电子",
        degree="工学",
        duration_years=4,
        is_enrollment=True,
        subject_evaluation="A",
        employment_rate=0.92,
        avg_salary=12000,
        description="培养电子信息系统设计、信号处理、通信工程等领域人才。"
    ),
    Major(
        code="081001",
        name="土木工程",
        category="土木",
        degree="工学",
        duration_years=4,
        is_enrollment=True,
        subject_evaluation="A+",
        employment_rate=0.88,
        avg_salary=10000,
        description="培养房屋建筑、桥梁隧道、岩土工程等领域设计施工人才。"
    ),
    Major(
        code="020101",
        name="经济学",
        category="经济",
        degree="经济学",
        duration_years=4,
        is_enrollment=True,
        subject_evaluation="A",
        employment_rate=0.90,
        avg_salary=11000,
        description="培养经济分析、金融投资、国际贸易等领域专业人才。"
    ),
    Major(
        code="050101",
        name="汉语言文学",
        category="文学",
        degree="文学",
        duration_years=4,
        is_enrollment=True,
        subject_evaluation="A+",
        employment_rate=0.85,
        avg_salary=8000,
        description="培养语言文字研究、文学创作、文化传播等领域人才。"
    ),
]

SAMPLE_SCORES = [
    # 北京大学 2025 上海
    AdmissionScore(year=2025, province="上海", university_code="10001", major_code="", 
                   major_name="院校投档线", score_min=613, score_avg=620, rank=108, batch="本科批"),
    AdmissionScore(year=2025, province="上海", university_code="10001", major_code="080501",
                   major_name="计算机科学与技术", score_min=618, score_avg=622, rank=95, batch="本科批"),
    # 清华大学 2025 上海
    AdmissionScore(year=2025, province="上海", university_code="10003", major_code="",
                   major_name="院校投档线", score_min=611, score_avg=617, rank=120, batch="本科批"),
    # 同济大学 2025 上海
    AdmissionScore(year=2025, province="上海", university_code="10247", major_code="",
                   major_name="院校投档线", score_min=565, score_avg=572, rank=5800, batch="本科批"),
    AdmissionScore(year=2025, province="上海", university_code="10247", major_code="081001",
                   major_name="土木工程", score_min=562, score_avg=568, rank=6100, batch="本科批"),
    # 复旦大学 2025 上海
    AdmissionScore(year=2025, province="上海", university_code="10246", major_code="",
                   major_name="院校投档线", score_min=605, score_avg=610, rank=280, batch="本科批"),
    # 上海交通大学 2025 上海
    AdmissionScore(year=2025, province="上海", university_code="10248", major_code="",
                   major_name="院校投档线", score_min=608, score_avg=614, rank=230, batch="本科批"),
    AdmissionScore(year=2025, province="上海", university_code="10248", major_code="080501",
                   major_name="计算机科学与技术", score_min=610, score_avg=615, rank=210, batch="本科批"),
]

SAMPLE_BATCH_LINES = [
    # 2025 上海 高考批次线
    BatchLine(year=2025, province="上海", batch="本科批", score_line=403, rank_line=50000),
]


if __name__ == "__main__":
    # 测试数据模型
    uni = SAMPLE_UNIVERSITIES[0]
    print(f"院校: {uni.name}, 代码: {uni.code}, 等级: {uni.get_display_level()}")
    
    major = SAMPLE_MAJORS[0]
    print(f"专业: {major.name}, 代码: {major.code}, 学科评估: {major.subject_evaluation}")
    
    score = SAMPLE_SCORES[0]
    print(f"分数: {score.year}年 {score.province} {score.university_code} 最低分{score.score_min}")
    
    strategy = VolunteerStrategy.default_strategy()
    print(f"默认策略: {strategy.principle.value}, 风险偏好: {strategy.risk_tolerance.value}")
