import os

BASE_URL = {
    "dev": "http://localhost:3000",
    "test": "http://localhost:3000",
    "prod": "http://prod-env.com"
}

def get_base_url():
    # 去系统里找 TEST_ENV 这个变量，如果没有，就默认用 "dev"
    env = os.getenv("TEST_ENV", "dev")
    return BASE_URL.get(env)