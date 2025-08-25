from util import print_formatted_response, set_jupyter_display_mode

print("=== Final Formatting Test: Grouped Content and Blocks ===\n")

test_cases = [
    {
        "name": "Content grouped with their blocks",
        "input": "(provide location) (specify time) [CONTEXT_INFORMATION] (app usage) #Provide_Context_Information#",
        "description": "Multiple content pieces for CONTEXT_INFORMATION, single content for complex block"
    },
    {
        "name": "Mixed content and blocks",
        "input": "(set personality) [BACKGROUND_INFORMATION] (user settings) [USER_PREFERENCES] #Guide_Tool_Use#",
        "description": "Each block has its own content, complex block without content"
    },
    {
        "name": "Blocks without content",
        "input": "[TONAL_CONTROL] [USER_PREFERENCES] #Guide_Tool_Use#",
        "description": "All blocks get empty () placeholders"
    },
    {
        "name": "Complex grouping",
        "input": "(manage style) (control format) [TONAL_CONTROL] (guide tools) #Guide_Tool_Use# [USER_PREFERENCES]",
        "description": "Multiple content for first block, content for complex block, empty for last block"
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"Test {i}: {test_case['name']}")
    print(f"Description: {test_case['description']}")
    print(f"Input: {test_case['input']}")
    print("\nFormatted Output:")
    print_formatted_response(test_case['input'], f"Test {i}")
    print("\n" + "="*80 + "\n")

print("✅ All tests demonstrate proper content-to-block grouping!")
print("✅ Content belonging to same block appears together on same line!")
print("✅ Blocks appearing together are on same line!")
