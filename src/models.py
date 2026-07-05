from dataclasses import dataclass, field


@dataclass
class Client:
    id: int | None = None
    name: str | None = None
    rating: float | None = None
    identity_verified: bool | None = None
    rule_checked: bool | None = None
    jobs_posted_count: int | None = None
    project_finished_rate: int | None = None
    profile_description: str | None = None


@dataclass
class JobSourceMetadata:
    url: str
    first_seen_at: str
    last_seen_at: str
    seen_count: int = 1


@dataclass
class JobMetadata:
    first_seen_at: str | None = None
    last_seen_at: str | None = None
    updated_at: str | None = None
    sources: list[JobSourceMetadata] = field(default_factory=list)


@dataclass
class Job:
    id: int
    title: str
    url: str
    category: str | None = None
    sub_category: str | None = None

    description: str | None = None
    reward: str | None = None

    application_deadline: str | None = None
    published_at: str | None = None
    delivery_deadline: str | None = None
    is_remote: bool | None = None

    application_count: int | None = None
    contract_count: int | None = None
    recruitment_count: int | None = None
    favorite_count: int | None = None

    client: Client | None = None
    metadata: JobMetadata | None = None


@dataclass
class AnalysisResult:
    """
    AIによる案件分析結果
    """

    # 数値評価
    reward_score: int
    competition_score: int
    ai_score: int
    continuity_score: int
    quality_score: int
    total_score: int

    # テキスト評価
    recommendation_reasons: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    application_strategy: list[str] = field(default_factory=list)
    overall_comment: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        """
        dict(JSON)からAnalysisResultを生成する
        """

        required_keys = [
            "reward_score",
            "competition_score",
            "ai_score",
            "continuity_score",
            "quality_score",
            "total_score",
            "recommendation_reasons",
            "concerns",
            "application_strategy",
            "overall_comment",
        ]

        missing = [key for key in required_keys if key not in data]
        if missing:
            raise ValueError(f"Missing required keys: {missing}")

        return cls(
            reward_score=data["reward_score"],
            competition_score=data["competition_score"],
            ai_score=data["ai_score"],
            continuity_score=data["continuity_score"],
            quality_score=data["quality_score"],
            total_score=data["total_score"],
            recommendation_reasons=data["recommendation_reasons"],
            concerns=data["concerns"],
            application_strategy=data["application_strategy"],
            overall_comment=data["overall_comment"],
        )

    def to_dict(self) -> dict:
        """
        AnalysisResultをdict(JSON)へ変換する
        """

        return {
            "reward_score": self.reward_score,
            "competition_score": self.competition_score,
            "ai_score": self.ai_score,
            "continuity_score": self.continuity_score,
            "quality_score": self.quality_score,
            "total_score": self.total_score,
            "recommendation_reasons": self.recommendation_reasons,
            "concerns": self.concerns,
            "application_strategy": self.application_strategy,
            "overall_comment": self.overall_comment,
        }
