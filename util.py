# util.py - System prompt generation utilities with refactored common patterns
from config import setup_env
from patterns import ModelConfig, OpenAIChat
from typing import Final, Optional, Dict, List, Tuple, Callable, Any
import json
import textwrap
import subprocess
import sys
import re

# Global model configuration - Single shared client
setup_env()
MODEL_CONFIG: Final = ModelConfig(
    model_id="gpt-5", temperature=0.8, max_tokens=3000
)
DEFAULT_MODEL = OpenAIChat(MODEL_CONFIG)


# ==================== SUPPORT FUNCTIONS ====================


def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and return JSON data from file."""
    with open(file_path, "r") as f:
        return json.load(f)


def load_text_file(file_path: str) -> str:
    """Load and return text content from file."""
    with open(file_path, "r") as f:
        return f.read()


def print_wrapped(text: str, width: int = 150, indent: str = "") -> None:
    """
    Print text with automatic line wrapping for long lines.
    
    Args:
        text: Text to print with wrapping
        width: Maximum line width (default 80)
        indent: String to indent wrapped lines (default "")
    """
    if not isinstance(text, str):
        print(text)
        return
    
    # Split by existing newlines to preserve intentional line breaks
    lines = text.split('\n')
    
    for line in lines:
        if len(line) <= width:
            print(line)
        else:
            # Wrap long lines
            wrapped_lines = textwrap.fill(
                line, 
                width=width,
                initial_indent=indent,
                subsequent_indent=indent,
                break_long_words=False,
                break_on_hyphens=False
            )
            print(wrapped_lines)


def play_notification_sound() -> None:
    """
    Play 3 notification sounds to indicate generation start.
    
    Tries multiple methods in order of preference:
    1. WSL-specific methods (Windows host audio) - 3 beeps
    2. Linux native audio systems - 3 beeps
    3. macOS system sounds - 3 plays
    4. Windows system beep - 3 beeps
    5. Terminal bell character - 3 bells
    6. Visual indicator fallback
    """
    try:
        # Check if running in WSL environment
        is_wsl = False
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                if 'microsoft' in version_info or 'wsl' in version_info:
                    is_wsl = True
        except (FileNotFoundError, PermissionError):
            pass
        
        if is_wsl:
            # WSL-specific approaches
            try:
                # Try to use Windows PowerShell to play 3 system sounds
                subprocess.run([
                    'powershell.exe', '-c', 
                    '[console]::beep(800,200); Start-Sleep -Milliseconds 100; [console]::beep(800,200); Start-Sleep -Milliseconds 100; [console]::beep(800,200)'
                ], check=False, capture_output=True, timeout=5)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            try:
                # Alternative: Use cmd.exe with 3 echo bells
                subprocess.run([
                    'cmd.exe', '/c', 'echo \a & timeout /t 0 >nul & echo \a & timeout /t 0 >nul & echo \a'
                ], check=False, capture_output=True, timeout=3)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            try:
                # Try Windows Media Player for a system sound
                subprocess.run([
                    'powershell.exe', '-c',
                    '(New-Object Media.SoundPlayer "C:\\Windows\\Media\\chimes.wav").PlaySync()'
                ], check=False, capture_output=True, timeout=3)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        
        elif sys.platform.startswith('linux'):
            # Native Linux - try multiple approaches
            try:
                # Try pactl for PulseAudio systems
                subprocess.run(['pactl', 'upload-sample', '/usr/share/sounds/alsa/Front_Left.wav', 'bell'],
                               check=False, capture_output=True, timeout=2)
                subprocess.run(['pactl', 'play-sample', 'bell'],
                               check=False, capture_output=True, timeout=2)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

            try:
                # Try speaker-test for ALSA
                subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'],
                               check=False, capture_output=True, timeout=3)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass

            try:
                # Try beep command if available (3 times)
                subprocess.run(['beep', '-f', '800', '-l', '200', '-r', '3', '-d', '100'],
                               check=False, capture_output=True, timeout=3)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
        elif sys.platform == 'darwin':
            # macOS - use afplay with system sound (3 times)
            try:
                import time
                for _ in range(3):
                    subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'],
                                   check=False, capture_output=True, timeout=2)
                    time.sleep(0.1)
                return
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
        elif sys.platform.startswith('win'):
            # Windows - use built-in beep (3 times)
            try:
                import winsound
                import time
                for _ in range(3):
                    winsound.Beep(800, 200)  # 800Hz for 200ms
                    time.sleep(0.1)  # 100ms pause between beeps
                return
            except ImportError:
                pass
        
        # Fallback: Terminal bell character (3 times)
        import time
        for _ in range(3):
            print('\a', end='', flush=True)
            time.sleep(0.1)
        
    except Exception:
        # Ultimate fallback: visual indicator with more emphasis
        print("\n🔔 ✅ TASK COMPLETED! 🔔")
        print("=" * 40)


def interactive_feedback_loop(
    generator_func: Callable,
    validator_func: Optional[Callable] = None,
    max_iterations: int = 5,
    task_name: str = "Processing",
    interactive: bool = False
) -> str:
    """
    Generic interactive feedback loop for iterative content generation.

    Args:
        generator_func: Function that generates content, receives
                       (iteration, feedback_history)
        validator_func: Optional validation function that returns
                       (is_valid, errors)
        max_iterations: Maximum number of iterations
        task_name: Name of the task for display
        interactive: If True, ask for user feedback. If False (default), 
                    run once and return result without user input

    Returns:
        Final generated response
    """
    iteration = 1
    feedback_history = []

    while iteration <= max_iterations:
        print(f"\n{'=' * 60}")
        print(f"{task_name.upper()} - Iteration {iteration}")
        print(f"{'=' * 60}")

        # Generate content
        try:
            # Play notification sound when generation starts
            
            response = generator_func(iteration, feedback_history)

            # Validate if validator provided
            if validator_func:
                is_valid, errors = validator_func(response)
                if not is_valid:
                    print("❌ Validation failed:")
                    for error in errors:
                        print(f"  - {error}")
                    # Add validation feedback for next iteration
                    validation_feedback = (
                        f"Iteration {iteration} validation errors: "
                        + "; ".join(errors)
                    )
                    feedback_history.append(validation_feedback)
                    iteration += 1
                    continue
                else:
                    print("✅ Validation passed!")

            print(f"===Response length:=== {len(response)} characters")
            print()
            print()
            print_wrapped(response, width=150)

        except Exception as e:
            print(f"Error in {task_name.lower()}: {str(e)}")
            response = f"Error: {str(e)}"

        print(f"\n{'=' * 60}")

        # If not interactive, return the first successful result
        if not interactive:
            print(f"\n{task_name} completed (non-interactive mode).")
            return response

        # Get user feedback (only in interactive mode)
        feedback = input(
            f"\nProvide feedback for {task_name.lower()} "
            "(or type 'good' to finish, 'stop' to end): "
        ).strip()

        if feedback == "":
            print(f"No feedback provided. {task_name} complete.")
            return response

        if feedback.lower() in ['done', 'good', 'good!', 'looks good',
                                'perfect']:
            print(f"\nGreat! {task_name} completed successfully.")
            return response

        if feedback.lower() in ['stop', 'quit', 'exit']:
            print(f"\nStopping {task_name.lower()}.")
            return response

        if feedback:
            feedback_history.append(f"Iteration {iteration}: {feedback}")
            print(f"Feedback recorded: {feedback}")
            print(f"Generating new {task_name.lower()} based on feedback...")

        iteration += 1

    print(f"\nReached maximum iterations ({max_iterations}). "
          "Returning final result.")
    return response


def retry_with_validation(
    generator_func: Callable,
    validator_func: Callable,
    max_retries: int = 3,
    task_name: str = "generation"
) -> str:
    """
    Retry content generation with validation until success or max retries.

    Args:
        generator_func: Function that generates content
        validator_func: Function that validates content, returns
                       (is_valid, errors)
        max_retries: Maximum number of retry attempts
        task_name: Name of the task for display

    Returns:
        Generated and validated content
    """
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Play notification sound when generation starts

            response = generator_func()
            play_notification_sound()
            is_valid, errors = validator_func(response)

            if is_valid:
                return response
            else:
                retry_count += 1
                print(f"❌ {task_name.capitalize()} failed validation "
                      f"(Attempt {retry_count}/{max_retries}):")
                for error in errors:
                    print(f"  - {error}")

                if retry_count < max_retries:
                    print(f"Retrying {task_name}...")
                else:
                    print(f"Max retries reached for {task_name}. "
                          "Using last response despite validation issues.")
                    return response

        except Exception as e:
            retry_count += 1
            print(f"Error in {task_name} "
                  f"(Attempt {retry_count}/{max_retries}): {str(e)}")
            if retry_count >= max_retries:
                return f"Error: {str(e)}"

    return response


# ==================== VALIDATION FUNCTIONS ====================


def validate_context_json(response_text: str) -> Tuple[
    bool, Optional[Dict], Optional[str]
]:
    """
    Validates that the response is valid JSON with the expected structure.
    Returns (is_valid, parsed_json, error_message)
    """
    try:
        # Try to extract JSON from response (in case there's extra text)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
        else:
            json_text = response_text.strip()

        # Parse JSON
        parsed = json.loads(json_text)

        # Validate structure
        if not isinstance(parsed, dict):
            return False, None, "Response is not a JSON object"

        if "contexts" not in parsed:
            return False, None, "Missing 'contexts' key in JSON"

        if not isinstance(parsed["contexts"], list):
            return False, None, "'contexts' must be an array"

        if len(parsed["contexts"]) != 5:
            return False, None, (
                f"Expected exactly 5 contexts, got {len(parsed['contexts'])}"
            )

        # Validate each context
        required_keys = [
            "user_name", "user_role", "user_personality",
            "what_they_are_doing_for_current_task", "conversation_flow"
        ]
        for i, context in enumerate(parsed["contexts"]):
            if not isinstance(context, dict):
                return False, None, f"Context {i + 1} is not an object"

            for key in required_keys:
                if key not in context:
                    return False, None, (
                        f"Context {i + 1} missing required key: {key}"
                    )

                if key == "conversation_flow":
                    if not isinstance(context[key], list):
                        return False, None, (
                            f"Context {i + 1} 'conversation_flow' must be an array"
                        )
                elif (not isinstance(context[key], str) or
                        not context[key].strip()):
                    return False, None, (
                        f"Context {i + 1} key '{key}' must be a "
                        "non-empty string"
                    )

        return True, parsed, None

    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, None, f"Validation error: {str(e)}"


def validate_structured_response(
    response: str, provided_inspiration: str
) -> Tuple[bool, List[str]]:
    """
    Validate the structured response from generate_block function.

    Args:
        response: Generated response to validate
        provided_inspiration: Original inspiration text to check against

    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Check 1: All 5 building block types mentioned
    required_blocks = [
        "[CONTEXT_INFORMATION]",
        "[TOOL_USE_INSTRUCTIONS]",
        "[USER_PREFERENCES]",
        "[BACKGROUND_INFORMATION]",
        "[TONAL_CONTROL]"
    ]

    missing_blocks = []
    for block in required_blocks:
        if block not in response:
            missing_blocks.append(block)

    if missing_blocks:
        errors.append(f"Missing building blocks: {', '.join(missing_blocks)}")

    # Check 2: Number of paragraphs (6-8)
    paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
    paragraphs = [p for p in paragraphs if p.strip().lower() != "you are"]

    paragraph_count = len(paragraphs)
    if paragraph_count < 6 or paragraph_count > 10:
        errors.append(
            f"Wrong number of paragraphs: {paragraph_count} (should be 6-8)"
        )

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_requirements_response(response: str, context: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate the requirements structure response according to complex_block_generation.md.
    
    Checks for:
    - Format: [BUILDING_BLOCK] (explanation) #Complex Block Name# (explanation) __unparaphrased ideas__
    - Mixed format with both parenthetical explanations and double underscore content
    - ALL 7 complex blocks present
    - Appropriate format choice based on semantic similarity
    - Proper paragraph count (6-8)
    - Concise explanations without redundant word lists
    - No specific tool references from user context
    """
    errors = []
    
    # Print response length    
    # Load complex blocks from JSON to check coverage
    complex_blocks = load_json_file("./complex_block.json")
    required_complex_blocks = list(complex_blocks.keys())

    # Check 1: Number of paragraphs (6-8)
    paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
    paragraphs = [p for p in paragraphs if p.strip().lower() != "you are"]

    paragraph_count = len(paragraphs)
    if paragraph_count < 6 or paragraph_count > 10:
        errors.append(
            f"Wrong number of paragraphs: {paragraph_count} (should be 6-8)"
        )

    # Check 2: Should contain building blocks with proper format
    building_blocks_found = re.findall(r'\[([A-Z_]+)\]', response)
    if not building_blocks_found:
        errors.append("Missing building block format [BLOCK_NAME]")

    # Check 3: Complex block coverage - ALL 7 types must be included
    missing_complex_blocks = []
    for complex_block_name in required_complex_blocks:
        # Check for #complex_block_name# format
        if f"#{complex_block_name}#" not in response:
            missing_complex_blocks.append(complex_block_name)

    # STRICT REQUIREMENT: ALL 7 complex blocks must be included
    if missing_complex_blocks:
        errors.append(
            f"Missing required complex blocks "
            f"({len(missing_complex_blocks)}/7 missing): "
            f"{', '.join(missing_complex_blocks)}"
        )

    # Check 4: Validate format appropriateness (separate vs merged)
    format_violations = []
    
    for paragraph in paragraphs:
        # Find building blocks and complex blocks in this paragraph
        building_matches = list(re.finditer(r'\[([A-Z_]+)\]', paragraph))
        complex_matches = list(re.finditer(r'#([^#]+)#', paragraph))
        
        for building_match in building_matches:
            building_name = building_match.group(1)
            building_pos = building_match.end()
            
            # Look for complex blocks after this building block
            for complex_match in complex_matches:
                if complex_match.start() > building_pos:
                    complex_name = complex_match.group(1)
                    complex_pos = complex_match.end()
                    
                    # Check what's between building block and complex block
                    between_text = paragraph[building_pos:complex_match.start()].strip()
                    
                    # Check what's after the complex block
                    after_text = paragraph[complex_pos:].strip()
                    
                    # Count explanations - both parenthetical and double underscore
                    explanations_count = 0
                    underscore_count = 0
                    
                    # Check for parenthetical explanations
                    if re.match(r'^\s*\([^)]+\)', between_text):
                        explanations_count += 1
                    if re.match(r'^\s*\([^)]+\)', after_text):
                        explanations_count += 1
                    
                    # Check for double underscore content (unparaphrased ideas)
                    if re.search(r'__[^_]+__', between_text):
                        underscore_count += 1
                    if re.search(r'__[^_]+__', after_text):
                        underscore_count += 1
                    
                    # Validate format choice - new format expects both () and __
                    # Expected format: [BLOCK] (explanation) #complex# (explanation) __unparaphrased__
                    total_content = explanations_count + underscore_count
                    
                    if explanations_count >= 1 and underscore_count >= 1:
                        # Good: Has both parenthetical explanations and unparaphrased content
                        pass
                    elif explanations_count >= 2 and underscore_count == 0:
                        # Acceptable: Traditional separate format without unparaphrased content
                        pass
                    elif explanations_count == 1 and underscore_count == 0:
                        # Acceptable: Traditional merged format
                        pass
                    elif total_content == 0:
                        format_violations.append(
                            f"Format issue: [{building_name}] and #{complex_name}# "
                            f"need explanations and/or unparaphrased content"
                        )
                    # Note: We're being permissive to allow various valid formats
                    break

    if format_violations:
        errors.extend(format_violations)

    # # Check 5: Look for oververbose explanations with redundant word lists
    # verbose_violations = []
    
    # # Pattern to detect redundant word lists like "analyze (examine, review, assess)"
    # redundant_pattern = r'\w+\s*\([^)]*,\s*[^)]*\)'
    
    # for paragraph in paragraphs:
    #     redundant_matches = re.findall(redundant_pattern, paragraph)
    #     if redundant_matches:
    #         for match in redundant_matches:
    #             verbose_violations.append(
    #                 f"Redundant word list detected: {match}"
    #             )
    
    # if verbose_violations:
    #     errors.append(
    #         f"Writing guideline violation: Avoid redundant word lists. "
    #         f"Found {len(verbose_violations)} instances of similar meaning words in parentheses."
    #     )

    # Check 6: Look for tool references from context (should be avoided)
    tool_violations = []
    
    if context:
        # Extract tool names from context conversation_flow
        try:
            import json
            context_data = json.loads(context)
            tools_from_context = set()
            
            # Extract tools from conversation_flow
            if "conversation_flow" in context_data:
                for flow_item in context_data["conversation_flow"]:
                    # Look for tools in parentheses like "(search_yelp)"
                    tool_matches = re.findall(r'\(([^)]+)\)', flow_item)
                    for tool in tool_matches:
                        tools_from_context.add(tool.strip())
            
            # Check if any tools from context are mentioned in response
            for tool in tools_from_context:
                if re.search(re.escape(tool), response, re.IGNORECASE):
                    tool_violations.append(f"Context tool reference found: {tool}")
                    
        except (json.JSONDecodeError, KeyError, TypeError):
            # If context parsing fails, skip tool validation
            pass
    
    if tool_violations:
        errors.append(
            "Writing guideline violation: Avoid mentioning specific tools from user context. "
            f"Found {len(tool_violations)} tool references."
        )

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_populate_response(response: str, context: Optional[str] = None) -> Tuple[bool, List[str]]:
    """
    Validate the populated block response according to block_population.md.
    
    Checks for:
    - No tool references from user context conversation_flow
    - No block name references like [CONTEXT_INFORMATION]
    - No adjective lists
    - Response length and quality
    """
    errors = []
    
    # Check 1: No block name references
    block_references = re.findall(r'\[([A-Z_]+)\]', response)
    if block_references:
        errors.append(f"Block name references found: {', '.join(block_references)}")
    
    complex_block_references = re.findall(r'#([^#]+)#', response)
    if complex_block_references:
        errors.append(f"Complex block references found: {', '.join(complex_block_references)}")
    
    # Check 2: No tool references from context
    tool_violations = []
    
    if context:
        try:
            import json
            context_data = json.loads(context)
            tools_from_context = set()
            
            # Extract tools from conversation_flow
            if "conversation_flow" in context_data:
                for flow_item in context_data["conversation_flow"]:
                    # Look for tools in parentheses like "(search_yelp)"
                    tool_matches = re.findall(r'\(([^)]+)\)', flow_item)
                    for tool in tool_matches:
                        tools_from_context.add(tool.strip())
            
            # Check if any tools from context are mentioned in response
            for tool in tools_from_context:
                if re.search(re.escape(tool), response, re.IGNORECASE):
                    tool_violations.append(f"Context tool reference found: {tool}")
                    
        except (json.JSONDecodeError, KeyError, TypeError):
            # If context parsing fails, skip tool validation
            pass
    
    if tool_violations:
        errors.append(
            "Writing guideline violation: Avoid mentioning specific tools from user context. "
            f"Found {len(tool_violations)} tool references."
        )
    
    # # Check 3: Look for adjective lists
    # adjective_list_pattern = r'\b\w+,\s+\w+,\s+(?:and\s+)?\w+'
    # adjective_matches = re.findall(adjective_list_pattern, response)
    # if adjective_matches:
    #     errors.append(f"Adjective lists found: {', '.join(adjective_matches[:3])}...")  # Show first 3
    
    is_valid = len(errors) == 0
    return is_valid, errors


# ==================== MAIN FUNCTIONS ====================


def generate_context(provided_inspiration: str, available_tools: str = "", current_system: str = "", interactive: bool = False) -> str:
    """Generate user contexts based on inspiration with optional interactive feedback."""
    
    # Load instruction template from markdown file
    instructions = load_text_file("./instructions/context_generation.md")
    system_prompt = instructions.replace("{available_tools}", available_tools).replace("{current_system}", current_system)

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        # Prepare the user message with feedback if available
        if feedback_history:
            user_message = f"""Create 5 diverse user contexts based on this inspiration: {provided_inspiration} that suitable for the following tools: {available_tools}

Previous feedback from user:
{chr(10).join(feedback_history)}

Please incorporate this feedback and generate improved contexts."""
        else:
            user_message = f"Create 5 diverse user contexts based on this inspiration: {provided_inspiration}"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # Use retry with validation
        def generator():
            return DEFAULT_MODEL.generate(messages)

        def validator(response):
            is_valid, parsed_json, error_message = validate_context_json(
                response
            )
            if is_valid:
                print("Generated Context Options:")
                return True, []
            else:
                return False, [error_message]

        return retry_with_validation(
            generator, validator, max_retries=3,
            task_name="context generation"
        )

    return interactive_feedback_loop(
        generate_content,
        max_iterations=10,
        task_name="Context Generation",
        interactive=interactive
    )


def generate_block(provided_inspiration: str, interactive: bool = False) -> str:
    """
    Generate a 6-8 paragraph system prompt using building block format
    with optional interactive feedback.

    Args:
        provided_inspiration: String containing ideas to incorporate
        interactive: If True, ask for user feedback. If False (default), 
                    run once and return result

    Returns:
        String: The generated structured system prompt
    """
    
    # Load instruction template and example from files
    instructions = load_text_file("./instructions/block_generation.md")
    build_block = load_text_file("./build_block.json")
    system_prompt = f"{instructions}\n\nReference example: {build_block}"

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = ""

        if provided_inspiration:
            user_message += f"""
Transform these ideas using different wording and distribute them naturally across the paragraphs. They can appear at any position within each paragraph.

Inspiration ideas to incorporate throughout the paragraphs is in bullet points.
INSPIRATION: 

{provided_inspiration}

ONLY RETURN THE BLOCK STRUCTURE, NO OTHER TEXT.
"""

        # Add feedback history if exists
        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))

        # Generate with retry and validation
        def generator():
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            return DEFAULT_MODEL.generate(messages)

        def validator(response):
            return validate_structured_response(
                response, provided_inspiration
            )

        return retry_with_validation(
            generator, validator, max_retries=3,
            task_name="structured prompt generation"
        )

    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Structured Prompt Generation",
        interactive=interactive
    )


def generate_complex_block(
    block_output: str, context: Optional[str] = None, interactive: bool = False
) -> str:
    """
    Add complex block identifiers from complex_block.json to existing
    building blocks.
    Format: #Block Name# (short explanation)
    Uses definitions and examples from the JSON file for accurate
    implementation.
    """

    # Load instruction template and complex block data
    instructions = load_text_file("./instructions/complex_block_generation.md")    
    system_prompt = instructions

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""

Context: {context if context else "General use"}

Add relevant complex block identifiers to this building block structure:

{block_output}

ONLY RETURN THE COMPLEX BLOCK STRUCTURE, NO OTHER TEXT.
"""

        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))

        # Generate with retry and validation
        def generator():
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            return DEFAULT_MODEL.generate(messages)

        def validator(response):
            return validate_requirements_response(response, context)

        return retry_with_validation(
            generator, validator, max_retries=3,
            task_name="complex block addition"
        )

    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Adding Complex Blocks",
        interactive=interactive
    )


def populate_block(
    complex_block: str, context: str, system_prompt_must: str, interactive: bool = False
) -> str:
    """
    Convert complex block structure into natural English system prompt.
    
    Args:
        complex_block: String containing complex block identifiers like 
                      [BLOCK_NAME] and #complex_name#
        context: String containing user context information
        system_prompt_must: Required text that must be included word-for-word
                           in the final system prompt
    
    Returns:
        String: Complete system prompt in natural English
    """
    
    # Load definitions only
    build_blocks = load_json_file("./build_block.json")
    complex_blocks = load_json_file("./complex_block.json")
    
    # Create definitions information for blocks
    block_definitions = ""
    for block_name, block_data in build_blocks.items():
        block_definitions += f"\n{block_name.upper()}:\n"
        block_definitions += f"Purpose: {block_data['what_it_is']}\n"
        block_definitions += f"Rule: {block_data['rule']}\n"
    
    complex_definitions = ""
    for block_name, block_data in complex_blocks.items():
        complex_definitions += f"\n{block_name}:\n"
        complex_definitions += f"Definition: {block_data['Definition']}\n"
    
    # Load instruction template
    instructions = load_text_file("./instructions/block_population.md")
    

    if system_prompt_must:
        system_prompt = f"{instructions}\n\nRequired text to include: {system_prompt_must}"
    else:
        system_prompt = f"{instructions}"
    
    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""
Convert this structured block format into a natural English system prompt:

CONTEXT:
{context}

REQUIRED TEXT (must include word-for-word): could be empty if not provided
"{system_prompt_must}"

STRUCTURED INPUT:
{complex_block}

ONLY RETURN THE SYSTEM PROMPT, NO OTHER TEXT.

"""
        
        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))
        
        # Generate with retry and validation
        def generator():
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message.strip()}
            ]
            return DEFAULT_MODEL.generate(messages)

        def validator(response):
            return validate_populate_response(response, context)

        return retry_with_validation(
            generator, validator, max_retries=3,
            task_name="block population"
        )
    
    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Populating Block Structure",
        interactive=interactive
    )


def add_system_info(
    complex_structure: str, context: str, system_settings: str, interactive: bool = False
) -> str:
    """
    Add 2-5 pieces of system setting information to the FIRST
    CONTEXT_INFORMATION block.

    Args:
        complex_structure: String containing the complex structure
                          (JSON format as string)
        context: String containing user context information
        system_settings: String containing system-specific settings and
                        configurations

    Returns:
        String: Enhanced complex structure with system info added to first
               CONTEXT_INFORMATION block
    """

    # Load instruction template
    instructions = load_text_file("./instructions/system_info_enhancement.md")
    system_prompt = instructions

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""
CONTEXT:
{context}

SYSTEM SETTINGS:
{system_settings}

COMPLEX STRUCTURE:
{complex_structure}

return the system prompt in the same format as the complex structure with the system info added to the first CONTEXT_INFORMATION block.

ONLY RETURN THE SYSTEM PROMPT, NO OTHER TEXT.

"""

        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message.strip()}
        ]

        return DEFAULT_MODEL.generate(messages)

    return interactive_feedback_loop(
        generate_content,
        max_iterations=3,
        task_name="Adding System Info to First Context Information Block",
        interactive=interactive
    )


# ==================== FORMALIZATION FUNCTIONS ====================


def formalize_system_prompt(
    system_prompt: str, interactive: bool = False
) -> str:
    """
    Convert system prompt to more direct, natural English with proper sentence subjects.
    Preserves all text inside quotation marks unchanged.
    
    Args:
        system_prompt: The system prompt to formalize
        interactive: If True, ask for user feedback. If False (default), 
                    run once and return result
    
    Returns:
        String: Formalized system prompt with natural English
    """
    
    # Load instruction template for formalization
    instructions = """You are a professional editor that converts system prompts into direct, natural English.

## Your Task
Transform the provided system prompt to use:
- Direct language with clear subjects in every sentence
- Natural English flow and structure
- Proper sentence construction with explicit subjects
- Professional but conversational tone

## Critical Rules
1. **NEVER change any text inside quotation marks** - preserve quoted content exactly as written
2. **Add clear subjects** to sentences that lack them (avoid starting with verbs)
3. **Use direct language** - replace passive voice with active voice where possible
4. **Maintain all original meaning** - only change language structure, not content
5. **Keep the same format structure** - preserve paragraphs, bullet points, etc.

## What NOT to Change
- Any text inside "quotation marks" - keep these exactly as written
- Technical terms, tool names, or specific instructions
- The overall structure and organization
- The core meaning or intent of any instruction"""

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""Please formalize this system prompt using direct, natural English with proper sentence subjects:

{system_prompt}

Remember: Do NOT change any text inside quotation marks. Only improve the language structure and directness."""

        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))

        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": user_message.strip()}
        ]

        return DEFAULT_MODEL.generate(messages)

    return interactive_feedback_loop(
        generate_content,
        max_iterations=3,
        task_name="Formalizing System Prompt",
        interactive=interactive
    )


# ==================== ANALYSIS FUNCTIONS ====================


def analyze_complex_block_coverage(response: str) -> Tuple[int, int]:
    """
    Analyze and display complex block coverage in the response.
    Shows which blocks are included and which are missing.
    """
    # Load complex blocks from JSON
    complex_blocks = load_json_file("./complex_block.json")

    all_complex_blocks = list(complex_blocks.keys())
    found_blocks = []
    missing_blocks = []

    print("=== COMPLEX BLOCK COVERAGE ANALYSIS ===")
    print(f"Total available complex blocks: {len(all_complex_blocks)}")
    print()

    for block_name in all_complex_blocks:
        if f"#{block_name}#" in response:
            found_blocks.append(block_name)
            print(f"✅ FOUND: {block_name}")
        else:
            missing_blocks.append(block_name)
            print(f"❌ MISSING: {block_name}")

    print()
    print(f"Coverage Summary: {len(found_blocks)}/{len(all_complex_blocks)} "
          "complex blocks included")
    coverage_pct = (len(found_blocks) / len(all_complex_blocks)) * 100
    print(f"Coverage Percentage: {coverage_pct:.1f}%")

    if missing_blocks:
        print(f"\nMissing blocks ({len(missing_blocks)}):")
        for block in missing_blocks:
            print(f"  - {block}")
            definition = complex_blocks[block]['Definition']
            print(f"    Definition: {definition}")

    return len(found_blocks), len(missing_blocks)


def show_all_complex_blocks():
    """Display all available complex blocks with their definitions."""
    complex_blocks = load_json_file("./complex_block.json")

    print("=== ALL AVAILABLE COMPLEX BLOCKS ===")
    for i, (block_name, block_data) in enumerate(complex_blocks.items(), 1):
        print(f"{i}. {block_name}")
        print(f"   Definition: {block_data['Definition']}")
        print(f"   Examples: {len(block_data['Examples'])} provided")
        print()



