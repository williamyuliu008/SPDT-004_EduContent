"""
高考志愿填报模块 - API 路由
FastAPI 风格接口定义
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional
from typing import List

from data_model import (
    University, Major, AdmissionScore,
    VolunteerStrategy, UserProfile, VolunteerPlan, MatchResult,
    StrategyPrinciple, RiskTolerance, MatchTier, RiskLevel,
    SAMPLE_UNIVERSITIES, SAMPLE_MAJORS, SAMPLE_SCORES
)
from matching_engine import MatchingEngine


# ============== 路由实例 ==============

router = APIRouter(prefix="/api/volunteer", tags=["志愿填报"])

# 全局引擎实例（实际应用中应注入依赖）
_engine: Optional[MatchingEngine] = None


def get_engine() -> MatchingEngine:
    """获取引擎实例"""
    global _engine
    if _engine is None:
        _engine = MatchingEngine(
            universities=SAMPLE_UNIVERSITIES,
            majors=SAMPLE_MAJORS,
            scores=SAMPLE_SCORES
        )
    return _engine


# ============== 请求/响应模型 ==============

class MatchRequest(BaseModel):
    """匹配请求"""
    score: int = Field(..., ge=0, le=800, description="高考分数")
    province: str = Field(..., description="高考省份")
    rank: int = Field(..., ge=1, description="省排名")
    subjects: List[str] = Field(default=[], description="选考科目")
    principle: str = Field(default="分数优先", description="优先策略")
    risk_tolerance: str = Field(default="稳健", description="风险偏好")
    preferred_provinces: List[str] = Field(default=[], description="偏好省份")
    preferred_levels: List[str] = Field(default=[], description="偏好等级")
    preferred_categories: List[str] = Field(default=[], description="偏好专业类别")


class UniversityResponse(BaseModel):
    """院校响应"""
    code: str
    name: str
    province: str
    city: str
    level: List[str]
    type: str
    rank_national: int
    rank_subject: dict
    website: str
    enrollment_count: int
    tuition_avg: int
    description: str


class MajorResponse(BaseModel):
    """专业响应"""
    code: str
    name: str
    category: str
    degree: str
    duration_years: int
    subject_evaluation: str
    employment_rate: float
    avg_salary: int
    description: str


class ScoreResponse(BaseModel):
    """分数响应"""
    year: int
    province: str
    university_code: str
    major_code: str
    major_name: str
    score_min: int
    score_avg: int
    rank: int
    batch: str
    enrollment_count: int


class MatchResultResponse(BaseModel):
    """匹配结果响应"""
    university: UniversityResponse
    major: Optional[MajorResponse]
    score_min: int
    score_avg: int
    probability: float
    risk_level: str
    score_difference: int
    tier: str
    reason: str


class VolunteerPlanResponse(BaseModel):
    """志愿方案响应"""
    user_score: int
    user_province: str
    user_rank: int
    strategy: dict
    chase: List[MatchResultResponse]
    secure: List[MatchResultResponse]
    safe: List[MatchResultResponse]
    buffer: List[MatchResultResponse]
    total_count: int
    create_time: str


# ============== API 路由定义 ==============

@router.get("/universities", response_model=List[UniversityResponse])
async def list_universities(
    q: Optional[str] = Query(None, description="搜索关键词"),
    province: Optional[str] = Query(None, description="省份筛选"),
    level: Optional[str] = Query(None, description="等级筛选"),
    type: Optional[str] = Query(None, description="类型筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量")
):
    """
    获取院校列表
    
    支持关键词搜索、省份/等级/类型筛选
    """
    engine = get_engine()
    results = engine.universities
    
    # 关键词搜索
    if q:
        q = q.lower()
        results = [u for u in results if q in u.name.lower() or q in u.code]
    
    # 省份筛选
    if province:
        results = [u for u in results if u.province == province]
    
    # 等级筛选
    if level:
        results = [u for u in results if level in u.level]
    
    # 类型筛选
    if type:
        results = [u for u in results if u.type == type]
    
    # 限制数量
    results = results[:limit]
    
    return [
        UniversityResponse(
            code=u.code,
            name=u.name,
            province=u.province,
            city=u.city,
            level=u.level,
            type=u.type,
            rank_national=u.rank_national,
            rank_subject=u.rank_subject,
            website=u.website,
            enrollment_count=u.enrollment_count,
            tuition_avg=u.tuition_avg,
            description=u.description
        )
        for u in results
    ]


@router.get("/universities/{code}", response_model=UniversityResponse)
async def get_university(code: str):
    """
    获取单个院校详情
    """
    engine = get_engine()
    university = engine.get_university_by_code(code)
    
    if not university:
        raise HTTPException(status_code=404, detail=f"院校 {code} 不存在")
    
    return UniversityResponse(
        code=university.code,
        name=university.name,
        province=university.province,
        city=university.city,
        level=university.level,
        type=university.type,
        rank_national=university.rank_national,
        rank_subject=university.rank_subject,
        website=university.website,
        enrollment_count=university.enrollment_count,
        tuition_avg=university.tuition_avg,
        description=university.description
    )


@router.get("/universities/{code}/majors", response_model=List[MajorResponse])
async def get_university_majors(code: str):
    """
    获取院校开设的专业列表
    """
    engine = get_engine()
    university = engine.get_university_by_code(code)
    
    if not university:
        raise HTTPException(status_code=404, detail=f"院校 {code} 不存在")
    
    # 实际应用中应返回该院校招生的专业
    # 这里返回示例数据
    return [
        MajorResponse(
            code=m.code,
            name=m.name,
            category=m.category,
            degree=m.degree,
            duration_years=m.duration_years,
            subject_evaluation=m.subject_evaluation,
            employment_rate=m.employment_rate,
            avg_salary=m.avg_salary,
            description=m.description
        )
        for m in engine.majors
    ]


@router.get("/majors", response_model=List[MajorResponse])
async def list_majors(
    category: Optional[str] = Query(None, description="专业类别"),
    degree: Optional[str] = Query(None, description="学位类型"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    获取专业列表
    """
    engine = get_engine()
    results = engine.majors
    
    if category:
        results = [m for m in results if m.category == category]
    
    if degree:
        results = [m for m in results if m.degree == degree]
    
    results = results[:limit]
    
    return [
        MajorResponse(
            code=m.code,
            name=m.name,
            category=m.category,
            degree=m.degree,
            duration_years=m.duration_years,
            subject_evaluation=m.subject_evaluation,
            employment_rate=m.employment_rate,
            avg_salary=m.avg_salary,
            description=m.description
        )
        for m in results
    ]


@router.get("/scores")
async def get_scores(
    year: int = Query(2025, description="年份"),
    province: str = Query(..., description="省份"),
    university_code: Optional[str] = Query(None, description="院校代码"),
    major_code: Optional[str] = Query(None, description="专业代码"),
    batch: Optional[str] = Query(None, description="批次")
):
    """
    获取录取分数数据
    """
    engine = get_engine()
    
    # 构建筛选条件
    def match_score(s: AdmissionScore) -> bool:
        if s.year != year:
            return False
        if s.province != province:
            return False
        if university_code and s.university_code != university_code:
            return False
        if major_code and s.major_code != major_code:
            return False
        if batch and s.batch != batch:
            return False
        return True
    
    results = [s for s in engine.scores if match_score(s)]
    
    return [
        {
            "year": s.year,
            "province": s.province,
            "university_code": s.university_code,
            "major_code": s.major_code,
            "major_name": s.major_name,
            "score_min": s.score_min,
            "score_avg": s.score_avg,
            "rank": s.rank,
            "batch": s.batch
        }
        for s in results
    ]


@router.post("/match", response_model=VolunteerPlanResponse)
async def match_volunteers(request: MatchRequest):
    """
    智能匹配志愿
    
    核心接口：根据用户分数和偏好生成志愿填报方案
    """
    engine = get_engine()
    
    # 构建用户档案
    user = UserProfile(
        province=request.province,
        score=request.score,
        rank=request.rank,
        subjects=request.subjects or ["语文", "数学", "外语"]
    )
    
    # 构建策略
    principle_map = {
        "分数优先": StrategyPrinciple.SCORE_FIRST,
        "院校优先": StrategyPrinciple.UNIVERSITY_FIRST,
        "专业优先": StrategyPrinciple.MAJOR_FIRST
    }
    risk_map = {
        "保守": RiskTolerance.CONSERVATIVE,
        "稳健": RiskTolerance.MODERATE,
        "激进": RiskTolerance.AGGRESSIVE
    }
    
    strategy = VolunteerStrategy(
        principle=principle_map.get(request.principle, StrategyPrinciple.SCORE_FIRST),
        risk_tolerance=risk_map.get(request.risk_tolerance, RiskTolerance.MODERATE),
        preferred_provinces=request.preferred_provinces,
        preferred_levels=request.preferred_levels or ["985", "211", "双一流"],
        preferred_categories=request.preferred_categories
    )
    
    # 生成方案
    plan = engine.generate_recommendations(user, strategy)
    
    def convert_result(r: MatchResult) -> MatchResultResponse:
        return MatchResultResponse(
            university=UniversityResponse(
                code=r.university.code,
                name=r.university.name,
                province=r.university.province,
                city=r.university.city,
                level=r.university.level,
                type=r.university.type,
                rank_national=r.university.rank_national,
                rank_subject=r.university.rank_subject,
                website=r.university.website,
                enrollment_count=r.university.enrollment_count,
                tuition_avg=r.university.tuition_avg,
                description=r.university.description
            ),
            major=None,
            score_min=r.admission_score.score_min,
            score_avg=r.admission_score.score_avg,
            probability=r.probability,
            risk_level=r.risk_level.value,
            score_difference=r.score_difference,
            tier=r.tier.value,
            reason=r.reason
        )
    
    return VolunteerPlanResponse(
        user_score=user.score,
        user_province=user.province,
        user_rank=user.rank,
        strategy={
            "principle": strategy.principle.value,
            "risk_tolerance": strategy.risk_tolerance.value,
            "preferred_provinces": strategy.preferred_provinces,
            "preferred_levels": strategy.preferred_levels
        },
        chase=[convert_result(r) for r in plan.tier_results.get(MatchTier.CHASE, [])],
        secure=[convert_result(r) for r in plan.tier_results.get(MatchTier.SECURE, [])],
        safe=[convert_result(r) for r in plan.tier_results.get(MatchTier.SAFE, [])],
        buffer=[convert_result(r) for r in plan.tier_results.get(MatchTier.BUFFER, [])],
        total_count=plan.total_volunteers,
        create_time=plan.create_time
    )


@router.get("/batch-locate")
async def locate_batch(
    score: int = Query(..., description="高考分数"),
    province: str = Query(..., description="省份")
):
    """
    批次定位查询
    
    根据分数确定可报考的批次
    """
    engine = get_engine()
    
    user = UserProfile(
        province=province,
        score=score,
        rank=0
    )
    
    result = engine.locate_batch(user)
    
    return result


# ============== 应用入口 ==============

def create_app():
    """创建 FastAPI 应用"""
    from fastapi import FastAPI
    
    app = FastAPI(
        title="高考志愿填报 API",
        description="智能志愿推荐服务",
        version="1.0.0"
    )
    
    app.include_router(router)
    
    return app


if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8007)
