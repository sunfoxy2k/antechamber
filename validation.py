from typing import Final

def check_min_length(text: str, min_length: int = 1500) -> bool:
    if len(text) < min_length:
        print(f"Response is too short. Expected at least {min_length} characters, got {len(text)}")

    return len(text) >= min_length

def check_if_con

def validate_response(text: str) -> bool:

    CHECK_LIST : Final = [check_min_length]

    for check_func in CHECK_LIST:
        
        if not check_func(text):
            return False
        
    return True
