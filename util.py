# util.py - System prompt generation utilities with refactored common patterns
from config import setup_env
from patterns import ModelConfig, OpenAIChat
from typing import Final, Optional, Dict, List, Tuple, Callable, Any
import json
import textwrap
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


def interactive_feedback_loop(
    generator_func: Callable,
    validator_func: Optional[Callable] = None,
    max_iterations: int = 5,
    task_name: str = "Processing"
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

            # Use formatted printing for better display
            if _use_jupyter_display:
                display_for_jupyter(response, task_name)
            else:
                print_formatted_response(response, task_name, max_width=80)

        except Exception as e:
            print(f"Error in {task_name.lower()}: {str(e)}")
            response = f"Error: {str(e)}"

        print(f"\n{'=' * 60}")

        # Get user feedback
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
            response = generator_func()
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
    if paragraph_count < 6 or paragraph_count > 8:
        errors.append(
            f"Wrong number of paragraphs: {paragraph_count} (should be 6-8)"
        )

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_requirements_response(response: str) -> Tuple[bool, List[str]]:
    """
    Validate the requirements structure response.
    Checks paragraphs, format, building blocks, and complex block coverage.
    """
    errors = []

    # Load complex blocks from JSON to check coverage
    complex_blocks = load_json_file("./complex_block.json")
    required_complex_blocks = list(complex_blocks.keys())

    # Check 1: Number of paragraphs (6-8)
    paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
    paragraphs = [p for p in paragraphs if p.strip().lower() != "you are"]

    paragraph_count = len(paragraphs)
    if paragraph_count < 6 or paragraph_count > 8:
        errors.append(
            f"Wrong number of paragraphs: {paragraph_count} (should be 6-8)"
        )

    # Check 2: Should contain building blocks
    if not re.search(r'\[[A-Z_]+\]', response):
        errors.append("Missing building block format [BLOCK_NAME]")

    # Check 3: Complex block coverage - ALL 7 types must be included
    missing_complex_blocks = []
    for complex_block_name in required_complex_blocks:
        # Check for #complex_block_name# format (separate format only)
        if f"#{complex_block_name}#" not in response:
            missing_complex_blocks.append(complex_block_name)

    # STRICT REQUIREMENT: ALL 7 complex blocks must be included
    if missing_complex_blocks:
        errors.append(
            f"Missing required complex blocks "
            f"({len(missing_complex_blocks)}/7 missing): "
            f"{', '.join(missing_complex_blocks)}"
        )

    # Check 4: At least 3 paragraphs must have 2 different complex blocks
    paragraphs_with_multiple_blocks = 0
    for paragraph in paragraphs:
        blocks_in_paragraph = set()
        for complex_block_name in required_complex_blocks:
            # Check separate format #block#
            if f"#{complex_block_name}#" in paragraph:
                blocks_in_paragraph.add(complex_block_name)

        # Check if this paragraph has 2 or more different complex blocks
        if len(blocks_in_paragraph) >= 2:
            paragraphs_with_multiple_blocks += 1

    if paragraphs_with_multiple_blocks < 3:
        errors.append(
            f"Insufficient paragraph complexity: only "
            f"{paragraphs_with_multiple_blocks} paragraphs have 2+ "
            "complex blocks (need at least 3)"
        )

    is_valid = len(errors) == 0
    return is_valid, errors


# ==================== MAIN FUNCTIONS ====================


def generate_context(provided_inspiration: str, available_tools: str = "", current_system: str = "") -> str:
    """Generate user contexts based on inspiration with interactive feedback."""
    
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
        task_name="Context Generation"
    )


def generate_block(provided_inspiration: str) -> str:
    """
    Generate a 6-8 paragraph system prompt using building block format
    with interactive feedback.

    Args:
        provided_inspiration: String containing ideas to incorporate

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

Inspiration ideas to incorporate throughout the paragraphs is in bullet points.
{provided_inspiration}

Transform these ideas using different wording and distribute them naturally across the paragraphs. They can appear at any position within each paragraph.
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
        task_name="Structured Prompt Generation"
    )


def generate_complex_block(
    block_output: str, context: Optional[str] = None
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
    complex_blocks = load_json_file("./complex_block.json")
    
    # Create detailed information about each complex block
    complex_block_info = ""
    for block_name, block_data in complex_blocks.items():
        complex_block_info += f"\n- {block_name}:\n"
        complex_block_info += f"  Definition: {block_data['Definition']}\n"
        examples_str = '; '.join(block_data['Examples'])
        complex_block_info += f"  Examples: {examples_str}\n"
    
    system_prompt = f"{instructions}\n\nAvailable complex blocks with definitions and examples (ALL MUST BE USED):{complex_block_info}"

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""
Add relevant complex block identifiers to this building block structure:

{block_output}

Context: {context if context else "General use"}
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
            return validate_requirements_response(response)

        return retry_with_validation(
            generator, validator, max_retries=3,
            task_name="complex block addition"
        )

    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Adding Complex Blocks"
    )


def populate_block(
    complex_block: str, context: str, system_prompt_must: str
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
    
    system_prompt = f"{instructions}\n\nRequired text to include: {system_prompt_must}\n\nBLOCK DEFINITIONS:\n{block_definitions}\n\nCOMPLEX BLOCK DEFINITIONS:\n{complex_definitions}"
    
    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""
Convert this structured block format into a natural English system prompt:

STRUCTURED INPUT:
{complex_block}

CONTEXT:
{context}

REQUIRED TEXT (must include word-for-word):
{system_prompt_must}

Focus on populate, address as YOU are for the system prompt, and the user is . Dont mention we, us. Should be objective. 
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
        max_iterations=5,
        task_name="Populating Block Structure"
    )


def add_system_info(
    complex_structure: str, context: str, system_settings: str
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
Add 2-5 pieces of system setting information to the FIRST CONTEXT_INFORMATION block:

COMPLEX STRUCTURE:
{complex_structure}

CONTEXT:
{context}

SYSTEM SETTINGS:
{system_settings}

Requirements:
- Add 2-5 pieces of system setting information to the FIRST CONTEXT_INFORMATION block only
- Generate relevant system info based on context and system settings
- Maintain exact structure and format
- Leave all other blocks unchanged
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
        task_name="Adding System Info to First Context Information Block"
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
            definition = complex_blocks[block]['Definition'][:100]
            print(f"    Definition: {definition}...")

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


# ==================== FORMATTING FUNCTIONS ====================


def parse_and_group_components(line: str) -> Dict:
    """
    Parse line and group content with their blocks properly.
    Returns dict with content_line and block_line.
    """
    # Find all components in order
    pattern = r'(\([^)]*\)|\[[^\]]+\]|#[^#]+#)'
    matches = re.findall(pattern, line)
    
    # Group content and blocks
    content_parts = []
    block_parts = []
    pending_content = []
    
    for match in matches:
        if match.startswith('(') and match.endswith(')'):
            # This is content
            content = match[1:-1]  # Remove parentheses
            pending_content.append(content)
        elif match.startswith('[') or match.startswith('#'):
            # This is a block
            if pending_content:
                # Group all pending content for this block
                if len(pending_content) == 1:
                    content_parts.append(f"({pending_content[0]})")
                else:
                    # Multiple content pieces for same block
                    grouped = " ".join([f"({c})" for c in pending_content])
                    content_parts.append(grouped)
                pending_content = []
            else:
                # Block without content
                content_parts.append("()")
            
            block_parts.append(match)
    
    # Handle any remaining content without blocks
    if pending_content:
        for content in pending_content:
            content_parts.append(f"({content})")
    
    return {
        'content_line': "  ".join(content_parts) if content_parts else "",
        'block_line': "  ".join(block_parts) if block_parts else ""
    }

def format_structured_output_final(text: str, max_width: int = 80) -> str:
    """
    Format structured output with proper grouping.
    Content belonging to same block stays together.
    """
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if not line.strip():
            formatted_lines.append('')
            continue
            
        # Check if line contains blocks
        if ('[' in line and ']' in line) or ('#' in line and line.count('#') >= 2):
            # Parse and group the structured line
            grouped = parse_and_group_components(line)
            
            # Add content line
            if grouped['content_line']:
                wrapped_content = textwrap.fill(grouped['content_line'], width=max_width,
                                              break_long_words=False, break_on_hyphens=False)
                formatted_lines.extend(wrapped_content.split('\n'))
            
            # Add block line
            if grouped['block_line']:
                wrapped_blocks = textwrap.fill(grouped['block_line'], width=max_width,
                                             break_long_words=False, break_on_hyphens=False)
                formatted_lines.extend(wrapped_blocks.split('\n'))
            
            formatted_lines.append('')  # Add spacing
            
        else:
            # Regular line wrapping
            wrapped = textwrap.fill(line, width=max_width, 
                                   break_long_words=False, 
                                   break_on_hyphens=False)
            formatted_lines.extend(wrapped.split('\n'))
    
    return '\n'.join(formatted_lines)

def print_formatted_response(response: str, task_name: str = "Response", max_width: int = 80):
    """
    Print response with proper formatting for Jupyter notebooks.
    
    Args:
        response: The response text to format
        task_name: Name of the task for the header
        max_width: Maximum line width
    """
    print(f"\n{'=' * min(60, max_width)}")
    print(f"Generated {task_name}:")
    print(f"{'=' * min(60, max_width)}")
    
    formatted_text = format_structured_output_final(response, max_width)
    print(formatted_text)
    
    print(f"{'=' * min(60, max_width)}")


def test_formatting():
    """Test the formatting functions with sample structured text."""
    sample_text = """[CONTEXT_INFORMATION] (provide current location, time, device state, and environment settings) #Provide_Context_Information# (specify current app usage and relevant application context)

[BACKGROUND_INFORMATION] (provide context and background) #Define_Personality_and_Tone# (set consistent character, discourage sycophancy, handle personal questions)

[TONAL_CONTROL] (manage response style) #Guide Tool Use and Response Formatting# (specify tool triggers, control lists vs prose formatting) [USER_PREFERENCES] (user specific preferences)"""
    
    print("=== FORMATTING TEST ===")
    print("\nOriginal text:")
    print("-" * 40)
    print(sample_text)
    
    print("\nFormatted text:")
    print("-" * 40)
    print_formatted_response(sample_text, "Structured Prompt", max_width=80)


def display_for_jupyter(response: str, task_name: str = "Response"):
    """
    Display formatted response optimized for Jupyter notebooks.
    Uses HTML formatting for better visual presentation.
    """
    try:
        from IPython.display import display, HTML
        
        # Format the response
        formatted_text = format_structured_output_final(response, max_width=100)
        
        # Create HTML with better styling
        html_content = f"""
        <div style="border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f9f9f9;">
            <h3 style="color: #4CAF50; margin-top: 0;">📝 {task_name}</h3>
            <pre style="white-space: pre-wrap; font-family: 'Monaco', 'Menlo', 'Consolas', monospace; 
                        background-color: #ffffff; padding: 10px; border-radius: 5px; 
                        border-left: 4px solid #4CAF50; overflow-x: auto; max-width: 100%;">
{formatted_text}
            </pre>
        </div>
        """
        
        display(HTML(html_content))
        
    except ImportError:
        # Fallback to regular print if not in Jupyter
        print_formatted_response(response, task_name, max_width=100)


def set_jupyter_display_mode():
    """
    Update the interactive_feedback_loop to use Jupyter-optimized display.
    Call this function when running in Jupyter notebooks.
    """
    global _use_jupyter_display
    _use_jupyter_display = True
    print("✅ Jupyter display mode enabled - responses will be formatted for notebooks")


# Global flag for display mode
_use_jupyter_display = False
