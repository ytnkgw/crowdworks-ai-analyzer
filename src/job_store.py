from datetime import date

from job_filter import should_exclude_by_deadline
from models import Job, JobMetadata, JobSourceMetadata


def build_job_index(jobs: list[Job]) -> dict[int, Job]:
    index: dict[int, Job] = {}

    for job in jobs:
        if job.id in index:
            raise ValueError(f"Duplicate job id found: {job.id}")
        index[job.id] = job

    return index


def has_meaningful_changes(existing_job: Job, new_job: Job) -> bool:
    fields_to_compare = (
        "title",
        "url",
        "category",
        "sub_category",
        "description",
        "reward",
        "application_deadline",
        "published_at",
        "delivery_deadline",
        "is_remote",
        "application_count",
        "contract_count",
        "recruitment_count",
        "favorite_count",
        "client",
    )

    for field_name in fields_to_compare:
        if getattr(existing_job, field_name) != getattr(new_job, field_name):
            return True

    return False


def initialize_job_metadata(job: Job, source_url: str, now: str) -> Job:
    if job.metadata is not None:
        return job

    job.metadata = JobMetadata()

    job.metadata.first_seen_at = now
    job.metadata.last_seen_at = now
    job.metadata.updated_at = now
    job.metadata.sources = [
        JobSourceMetadata(
            url=source_url,
            first_seen_at=now,
            last_seen_at=now,
            seen_count=1,
        )
    ]

    return job


def update_seen_metadata(job: Job, source_url: str, now: str) -> Job:
    if job.metadata is None:
        return initialize_job_metadata(job, source_url, now)

    job.metadata.last_seen_at = now

    for source in job.metadata.sources:
        if source.url != source_url:
            continue

        source.last_seen_at = now
        source.seen_count += 1
        return job

    job.metadata.sources.append(
        JobSourceMetadata(
            url=source_url,
            first_seen_at=now,
            last_seen_at=now,
            seen_count=1,
        )
    )
    return job


def update_job_if_changed(existing_job: Job, new_job: Job, now: str) -> Job:
    if not has_meaningful_changes(existing_job, new_job):
        return existing_job

    existing_job.title = new_job.title
    existing_job.url = new_job.url
    existing_job.category = new_job.category
    existing_job.sub_category = new_job.sub_category
    existing_job.description = new_job.description
    existing_job.reward = new_job.reward
    existing_job.application_deadline = new_job.application_deadline
    existing_job.published_at = new_job.published_at
    existing_job.delivery_deadline = new_job.delivery_deadline
    existing_job.is_remote = new_job.is_remote
    existing_job.application_count = new_job.application_count
    existing_job.contract_count = new_job.contract_count
    existing_job.recruitment_count = new_job.recruitment_count
    existing_job.favorite_count = new_job.favorite_count
    existing_job.client = new_job.client

    if existing_job.metadata is not None:
        existing_job.metadata.updated_at = now

    return existing_job


def merge_jobs(
    existing_jobs: list[Job],
    collected_jobs: list[Job],
    source_url: str,
    now: str,
) -> list[Job]:
    merged_jobs = list(existing_jobs)
    existing_index = build_job_index(existing_jobs)

    for collected_job in collected_jobs:
        existing_job = existing_index.get(collected_job.id)
        if existing_job is None:
            initialize_job_metadata(collected_job, source_url, now)
            merged_jobs.append(collected_job)
            existing_index[collected_job.id] = collected_job
            continue

        update_seen_metadata(existing_job, source_url, now)
        update_job_if_changed(existing_job, collected_job, now)

    return merged_jobs


def remove_expired_jobs(jobs: list[Job], today: date | None = None) -> list[Job]:
    filtered: list[Job] = []

    for job in jobs:
        if should_exclude_by_deadline(job.application_deadline, today=today):
            continue
        filtered.append(job)

    return filtered


def update_job_store(
    existing_jobs: list[Job],
    collected_jobs: list[Job],
    source_url: str,
    now: str,
    today: date | None = None,
) -> list[Job]:
    merged_jobs = merge_jobs(existing_jobs, collected_jobs, source_url, now)
    return remove_expired_jobs(merged_jobs, today=today)
