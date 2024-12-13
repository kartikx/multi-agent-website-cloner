import os

llm_config = {
    "config_list": [{
        "model": "gpt-4o-mini",
        "api_type": "openai",
        "api_key": os.environ.get("OPENAI_KEY"),
    }]
}

context_variables = {
    "target_file_location": "",
    "html_file_location": "",
    "html_code": "",
    "num_tries": 0,
    "attempt_code": None,
    "feedback": None,
}
