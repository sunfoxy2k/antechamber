# Example usage for Jupyter notebooks
from util import set_jupyter_display_mode, display_for_jupyter, print_formatted_response

# Enable Jupyter display mode
set_jupyter_display_mode()

# Example structured text
sample_response = """[CONTEXT_INFORMATION] (provide current location, time, device state, and environment settings) #Provide_Context_Information# (specify current app usage and relevant application context)

[BACKGROUND_INFORMATION] (provide context and background) #Define_Personality_and_Tone# (set consistent character, discourage sycophancy, handle personal questions)

[TONAL_CONTROL] (manage response style) #Guide Tool Use and Response Formatting# (specify tool triggers, control lists vs prose formatting)

[USER_PREFERENCES] (user specific preferences and settings) #Set Clear Guardrails# (define safety boundaries and refusal protocols)"""

# Test both display methods
print("=== Regular Terminal Display ===")
print_formatted_response(sample_response, "Structured Prompt Example")

print("\n=== Jupyter Notebook Display ===")
display_for_jupyter(sample_response, "Structured Prompt Example")
