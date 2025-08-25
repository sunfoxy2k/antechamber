from util import print_formatted_response, set_jupyter_display_mode

# Test cases showing the 1:1 mapping
test_cases = [
    # Case 1: Each content has its own block
    "[CONTEXT_INFORMATION] (provide location and time) #Provide_Context_Information#",
    
    # Case 2: Blocks without content get empty ()
    "[BACKGROUND_INFORMATION] #Define_Personality_and_Tone#",
    
    # Case 3: Multiple blocks each get their own empty ()
    "[TONAL_CONTROL] [USER_PREFERENCES] #Guide_Tool_Use#",
    
    # Case 4: Mixed content and blocks
    "(set user preferences) [USER_PREFERENCES] (manage response style) #Guide_Tool_Use# [CONTEXT_INFORMATION]"
]

print("=== Testing 1:1 Content-to-Block Mapping ===\n")

for i, test_case in enumerate(test_cases, 1):
    print(f"Test Case {i}:")
    print(f"Input: {test_case}")
    print("Formatted Output:")
    print_formatted_response(test_case, f"Test Case {i}")
    print("\n" + "="*80 + "\n")
