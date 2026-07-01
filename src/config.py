import os

CW_BASE_URL = "https://crowdworks.jp"

CW_JOB_DETAIL_URL = f"{CW_BASE_URL}/public/jobs"

CW_JOB_LIST_URL = f"{CW_BASE_URL}/public/jobs/group/ai_bpo"

OUTPUT_DIR = "output"

DEBUG_DIR = "debug"

HTML_FILENAME = "crowdworks_ai_bpo.html"

REQUEST_TIMEOUT = 30

OPENAI_API_KEY = os.getenv("CW_AI_ANALYZER_OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
