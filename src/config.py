import os

CW_BASE_URL = "https://crowdworks.jp"

CW_JOB_DETAIL_URL = f"{CW_BASE_URL}/public/jobs"

OUTPUT_DIR = "output"

OUTPUT_JOBS_FILENAME = "jobs.json"
OUTPUT_ANALYSIS_RESULTS_FILENAME = "analysis_results.json"
OUTPUT_RANKED_JOBS_FILENAME = "ranked_jobs.json"
OUTPUT_RANKED_REPORT_FILENAME = "ranked_jobs_report.md"

DEBUG_DIR = "debug"

HTML_FILENAME = "crowdworks_ai_bpo.html"

REQUEST_TIMEOUT = 30

OPENAI_API_KEY = os.getenv("CW_AI_ANALYZER_OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
