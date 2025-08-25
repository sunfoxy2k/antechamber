# util.py - System prompt generation utilities with refactored common patterns
from config import setup_env
from patterns import ModelConfig, OpenAIChat
from typing import Final, Optional, Dict, List, Tuple, Callable, Any
import json
import re

# Global model configuration
setup_env()
MODEL_CONFIG: Final = ModelConfig(
    model_id="gpt-5", temperature=0.8, max_tokens=3000
)
DEFAULT_MODEL = OpenAIChat(MODEL_CONFIG)


# ==================== SUPPORT FUNCTIONS ====================


def create_model(
    model_id: str = "gpt-5", temperature: float = 0.7, max_tokens: int = 2500
) -> OpenAIChat:
    """Create an OpenAI model with specified configuration."""
    config = ModelConfig(
        model_id=model_id, temperature=temperature, max_tokens=max_tokens
    )
    return OpenAIChat(config)


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
        print(f"\n{'='*60}")
        print(f"{task_name.upper()} - Iteration {iteration}")
        print(f"{'='*60}")

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

            print(f"Generated {task_name}:")
            print("-" * 40)
            print(response)
            print("-" * 40)

        except Exception as e:
            print(f"Error in {task_name.lower()}: {str(e)}")
            response = f"Error: {str(e)}"

        print(f"\n{'='*60}")

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
            "user_role", "user_personality",
            "what_they_are_doing_for_current_task"
        ]
        for i, context in enumerate(parsed["contexts"]):
            if not isinstance(context, dict):
                return False, None, f"Context {i+1} is not an object"

            for key in required_keys:
                if key not in context:
                    return False, None, (
                        f"Context {i+1} missing required key: {key}"
                    )

                if (not isinstance(context[key], str) or
                        not context[key].strip()):
                    return False, None, (
                        f"Context {i+1} key '{key}' must be a "
                        "non-empty string"
                    )

        return True, parsed, None

    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, None, f"Validation error: {str(e)}"


def validate_structured_response(
    response: str, provided_inspiration: str, model: OpenAIChat
) -> Tuple[bool, List[str]]:
    """
    Validate the structured response from generate_block function.

    Args:
        response: Generated response to validate
        provided_inspiration: Original inspiration text to check against
        model: OpenAI model for content validation

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

    # Check 3: ChatGPT validation of inspiration content
    if provided_inspiration and provided_inspiration.strip():
        validation_prompt = f"""Check if this generated response contains all the key ideas from the provided inspiration.

Generated Response:
{response}

Original Inspiration:
{provided_inspiration}

Answer with just "YES" if all inspiration ideas are incorporated (using different wording is fine), or "NO" followed by what's missing."""

        try:
            validation_messages = [
                {"role": "user", "content": validation_prompt}
            ]
            validation_response = model.generate(validation_messages)

            if not validation_response.strip().upper().startswith("YES"):
                errors.append(
                    f"Inspiration content validation failed: "
                    f"{validation_response}"
                )
        except Exception as e:
            errors.append(f"Could not validate inspiration content: {str(e)}")

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_requirements_response(
    response: str, model: OpenAIChat
) -> Tuple[bool, List[str]]:
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

    # Check 2: Format validation - should have mixed format
    # (both #block# and merged [BLOCK#complex])
    has_separate_format = bool(re.search(r'#[^#]+#', response))
    has_merged_format = bool(re.search(r'\[[A-Z_]+#[A-Za-z_\s]+\]', response))

    if not has_separate_format and not has_merged_format:
        errors.append(
            "Missing both separate #block# and merged [BLOCK#complex] formats"
        )
    elif not has_separate_format:
        errors.append("Missing separate #block# format")
    elif not has_merged_format:
        errors.append("Missing merged [BLOCK#complex] format")

    # Check 3: Should still contain building blocks
    # (either standalone or merged)
    if (not re.search(r'\[[A-Z_]+\]', response) and
            not re.search(r'\[[A-Z_]+#', response)):
        errors.append("Missing building block format [BLOCK_NAME]")

    # Check 4: Complex block coverage - Python check for ALL types included
    missing_complex_blocks = []
    for complex_block_name in required_complex_blocks:
        short_name = (complex_block_name.replace(" ", "_")
                      .replace(",", "").replace("-", "_"))
        found_separate = f"#{complex_block_name}#" in response
        found_merged = (f"#{complex_block_name}" in response or
                        f"#{short_name}" in response or
                        complex_block_name.replace(" ", "_") in response)

        if not found_separate and not found_merged:
            missing_complex_blocks.append(complex_block_name)

    # STRICT REQUIREMENT: ALL 7 complex blocks must be included
    if missing_complex_blocks:
        errors.append(
            f"Missing required complex blocks "
            f"({len(missing_complex_blocks)}/7 missing): "
            f"{', '.join(missing_complex_blocks)}"
        )

    # Check 5: Verify we have exactly all 7 complex blocks
    found_complex_blocks = []
    for complex_block_name in required_complex_blocks:
        short_name = (complex_block_name.replace(" ", "_")
                      .replace(",", "").replace("-", "_"))
        found_separate = f"#{complex_block_name}#" in response
        found_merged = (f"#{complex_block_name}" in response or
                        f"#{short_name}" in response or
                        complex_block_name.replace(" ", "_") in response)

        if found_separate or found_merged:
            found_complex_blocks.append(complex_block_name)

    if len(found_complex_blocks) != 7:
        errors.append(
            f"Incomplete complex block coverage: "
            f"{len(found_complex_blocks)}/7 complex blocks found "
            "(ALL 7 REQUIRED)"
        )

    # Check 6: At least 3 paragraphs must have 2 different complex blocks
    paragraphs_with_multiple_blocks = 0
    for paragraph in paragraphs:
        blocks_in_paragraph = set()
        for complex_block_name in required_complex_blocks:
            short_name = (complex_block_name.replace(" ", "_")
                          .replace(",", "").replace("-", "_"))

            # Check separate format #block#
            if f"#{complex_block_name}#" in paragraph:
                blocks_in_paragraph.add(complex_block_name)

            # Check merged format [BLOCK#complex]
            elif (f"#{complex_block_name}" in paragraph or
                  f"#{short_name}" in paragraph or
                  complex_block_name.replace(" ", "_") in paragraph):
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


def generate_context(provided_inspiration: str) -> str:
    """Generate user contexts based on inspiration with interactive feedback."""

    system_prompt = """You are a creative context generator that creates diverse user personas and scenarios based on inspiration.

CRITICAL: You MUST respond with ONLY valid JSON. Do NOT include any explanatory text, markdown formatting, or additional commentary before or after the JSON. Your entire response must be parseable JSON.

Your task is to generate a JSON structure with exactly 5 diverse options, each containing:
- user_role: The role, identity, or life situation of the user
- user_personality: Key personality traits and characteristics
- what_they_are_doing_for_current_task: Specific current activity or task they're engaged in

IMPORTANT: Generate a MIX of both WORK-RELATED and CASUAL DAY-TO-DAY contexts to show the full range of possibilities.

Requirements:
1. Generate exactly 5 distinct options
2. Each option must be significantly different from the others
3. Include BOTH casual/personal contexts
4. Vary across different settings, personality types, and task complexity
5. Make each option realistic and relatable
6. Ensure diversity in life situations

RESPONSE FORMAT - Return ONLY this exact JSON structure with NO additional text:
{
  "contexts": [
    {
      "user_role": "string",
      "user_personality": "string",
      "what_they_are_doing_for_current_task": "string"
    }
  ]
}

Create authentic, varied personas spanning:

CASUAL DAY-TO-DAY CONTEXTS:
- Personal roles: Parent, student, hobbyist, retiree, homeowner, pet owner, etc.
- Daily activities: Household management, personal projects, hobbies, fitness, learning, etc.
- Life situations: Moving homes, planning events, organizing spaces, pursuing interests, etc.

PERSONALITY VARIETY:
- Analytical, creative, detail-oriented, big-picture, social, introverted, practical, dreamer, organized, spontaneous, etc.

REMINDER: Respond with ONLY the JSON object. No explanations, no markdown, no additional text."""

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        # Prepare the user message with feedback if available
        if feedback_history:
            user_message = f"""Create 5 diverse user contexts based on this inspiration: {provided_inspiration}

Previous feedback from user:
{chr(10).join(feedback_history)}

Please incorporate this feedback and generate improved contexts."""
        else:
            user_message = (
                f"Create 5 diverse user contexts based on this inspiration: "
                f"{provided_inspiration}"
            )

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
                print(json.dumps(parsed_json, indent=2))
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

    build_block = load_text_file("./build_block.json")

    # Base system prompt for generating structured prompts
    system_prompt = f"""You are a system prompt generator that creates structured prompts using building block format.

Create 6 to 8 paragraphs using building block format.

Format Structure:
Each paragraph should follow patterns like:
- [block name] [block name] (content that paraphrases ideas) [block name]
- [block name] (content with paraphrased ideas) [block name] [block name]
- (content incorporating paraphrased ideas) [block name] [block name] [block name]
- [block name] [block name] [block name]
- [block name] [block name]

The order of block names is completely flexible - you can place them at the beginning, middle, end, or mixed throughout each paragraph as makes sense for natural flow.

Requirements:
1. ONLY SHOW AS BLOCK NAME and (paraphrased ideas) in the paragraph, do not have any other text in the paragraph.
2. Create 6 to 8 paragraphs (choose the number that works best for the content)
3. Each paragraph uses 2-3 building block references. At least 1 paragraph only has [block name] [block name].
4. Adapt everything to be suitable for the given context
5. This is to generate a system prompt, so structure it appropriately
6. Use ONLY these specific building block names:
   - [CONTEXT_INFORMATION]
   - [TOOL_USE_INSTRUCTIONS]
   - [USER_PREFERENCES]
   - [BACKGROUND_INFORMATION]
   - [TONAL_CONTROL]
7. Reference this as example {build_block}
8. (text inside round brackets) is paraphrased from inspiration ideas only and should be a full paraphase, and can easily identify as a paraphrased version of the inspiration ideas. Should have 1 to 1 map between paraphase and inspiration ideas.
9. THERE MUST BE AT LEAST 2 PARAGRAPHS that is [block name] [block name] [block name] only without paraphrased ideas.

Generate the system prompt using the flexible building block format"""

    # Create model with 2500 token limit
    structured_model = create_model(
        model_id="gpt-5", temperature=0.7, max_tokens=2500
    )

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
            return structured_model.generate(messages)

        def validator(response):
            return validate_structured_response(
                response, provided_inspiration, structured_model
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

    # Load complex blocks from JSON with definitions and examples
    complex_blocks = load_json_file("./complex_block.json")

    # Create detailed information about each complex block
    complex_block_info = ""
    for block_name, block_data in complex_blocks.items():
        complex_block_info += f"\n- {block_name}:\n"
        complex_block_info += f"  Definition: {block_data['Definition']}\n"
        examples_str = '; '.join(block_data['Examples'])
        complex_block_info += f"  Examples: {examples_str}\n"

    system_prompt = f"""You are a system prompt processor that adds complex block identifiers to building block structures using MIXED FORMAT.

Your task:
1. Keep the existing paragraph structure EXACTLY as is
2. Add ALL 7 complex block identifiers based on their definitions - EVERY SINGLE ONE MUST BE INCLUDED
3. Use MIXED FORMAT: 30-40% merged format, 60-70% separate format
4. Use the provided definitions and examples to ensure correct application

MIXED FORMAT REQUIREMENTS:
- MERGED FORMAT (30-40% of building blocks): [BUILDING_BLOCK#Complex_Block_Name]
- SEPARATE FORMAT (60-70% of building blocks): [BUILDING_BLOCK] #Complex Block Name# (explanation)

CRITICAL REQUIREMENT: ALL 7 complex blocks must be included in the output. No exceptions.

Available complex blocks with definitions and examples (ALL MUST BE USED):
{complex_block_info}

Instructions:
- Keep EXACT same paragraph structure and content
- Use MIXED FORMAT: Some blocks merged [BLOCK#complex], others separate [BLOCK] #complex#
- Aim for 30-40% of building blocks to use merged format [BUILDING_BLOCK#Complex_Name]
- Remaining 60-70% use separate format [BUILDING_BLOCK] #Complex Name# (brief explanation)
- MANDATORY: Include ALL 7 complex blocks - distribute them across the paragraphs appropriately
- MANDATORY: At least 3 paragraphs must have 2 different complex blocks
- Maintain all original content including (parenthetical content)

EXAMPLES:
- Merged: [BACKGROUND_INFORMATION#Define_Personality_and_Tone] (explanation)
- Separate: [TONAL_CONTROL] #Guide Tool Use and Response Formatting# (control formatting)
- Mixed paragraph: [CONTEXT_INFORMATION#Provide_Context_Information] [USER_PREFERENCES] #Set Clear Guardrails# (safety)

VALIDATION: The output will be checked to ensure:
- ALL 7 complex blocks are present
- At least 3 paragraphs have 2 different complex blocks
- Mixed format used (30-40% merged, 60-70% separate)
Missing any requirement will cause validation failure.

Process the building block structure now and ensure ALL 7 complex blocks are included with proper mixed format distribution."""

    structured_model = create_model(
        model_id="gpt-5", temperature=0.7, max_tokens=2500
    )

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
            return structured_model.generate(messages)

        def validator(response):
            return validate_requirements_response(response, structured_model)

        return retry_with_validation(
            generator, validator, max_retries=3,
            task_name="complex block addition"
        )

    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Adding Complex Blocks"
    )


def populate_content_from_complex_block_improved(
    complex_block: str, context: Optional[str] = None
) -> str:
    """
    Generate actual system prompt content from complex block identifiers.
    Uses both structure.json and complex_block.json for accurate content
    generation.

    Args:
        complex_block: String containing complex block identifiers like
                      #Block Name#
        context: Optional context information to tailor the content

    Returns:
        String: The populated system prompt with actual content
    """

    # Load both structure definitions and complex block definitions
    complex_blocks = load_json_file("./complex_block.json")

    # Extract context information for tailoring
    context_info = ""
    if context:
        context_info = f"Context: {context}"

    # Create detailed complex block information
    complex_block_info = ""
    for block_name, block_data in complex_blocks.items():
        complex_block_info += f"\n- {block_name}:\n"
        complex_block_info += f"  Definition: {block_data['Definition']}\n"
        examples_str = '; '.join(block_data['Examples'])
        complex_block_info += f"  Examples: {examples_str}\n"

    # System prompt for generating actual content
    system_prompt = f"""You are a system prompt content generator that converts complex block identifiers into actual system prompt content.

Your task:
1. Replace each complex block identifier (like #Block Name#) with actual system prompt content
2. Use the provided definitions and examples from complex_block.json for each block
3. Use structure.json for additional technical details if needed
4. Tailor the content to be suitable for the given context
5. Follow the format: "actual_content [complexity_block]" where complexity_block is the original identifier
6. Generate natural, coherent system prompt content that flows well

Available complex block definitions and examples:
{complex_block_info}

{context_info}

Instructions:
- Keep the exact same paragraph structure as the input
- Replace each #identifier# with appropriate content based on its definition followed by [complexity_block]
- Content should be natural system prompt instructions that implement the definition
- Use the examples provided to understand how to apply each block correctly
- Tailor examples and language to the provided context
- Maintain coherent flow between sentences
- Each piece of content should be actionable system prompt instructions

Process the provided complex block structure now."""

    # Create model for content generation
    content_model = create_model(
        model_id="gpt-4", temperature=0.7, max_tokens=3000
    )

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""
Please convert each complex block identifier into actual system prompt content while maintaining the exact same structure.

Here is the complex block structure to populate:

{complex_block}

Remember to:
- Replace each #identifier# with relevant content based on its definition + [complexity_block]
- Keep all parenthetical content unchanged
- Use the definitions and examples from complex_block.json to ensure accuracy
- Tailor content to the provided context
- Make content actionable and clear
- Maintain natural flow
"""

        # Add feedback history if exists
        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message.strip()}
        ]

        return content_model.generate(messages)

    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Populating Content From Complex Block"
    )


def populate_content_from_complex_block(
    complex_block: str, context: Optional[str] = None
) -> str:
    """
    Generate actual system prompt content from complex block identifiers.

    Args:
        complex_block: String containing complex block identifiers like
                      [background_information@dynamic_behavior_scaling@
                       complexity_assessment]
        context: Optional context information to tailor the content

    Returns:
        String: The populated system prompt with actual content
    """

    requirement_structure_explain = load_json_file("./structure.json")[
        'requirements'
    ]

    # Extract context information for tailoring
    context_info = ""
    if context:
        context_info = f"Context: {context}"

    # System prompt for generating actual content
    system_prompt = f"""You are a system prompt content generator that converts complex block identifiers into actual system prompt content.

Your task:
1. Replace each complex block identifier (like [background_information@dynamic_behavior_scaling@complexity_assessment]) with actual system prompt content
2. Use the provided explanations and examples from the requirement structure
3. Tailor the content to be suitable for the given context
4. Follow the format: "actual_content [complexity_block]" where complexity_block is the original identifier
5. Generate natural, coherent system prompt content that flows well

Available requirement explanations and examples:
{json.dumps(requirement_structure_explain, indent=2)}

{context_info}

Instructions:
- Keep the exact same paragraph structure as the input
- Replace each [identifier] with appropriate content followed by [complexity_block]
- Content should be natural system prompt instructions
- Tailor examples and language to the provided context
- Maintain coherent flow between sentences
- Each piece of content should be actionable system prompt instructions

Process the provided complex block structure now."""

    # Create model for content generation
    content_model = create_model(
        model_id="gpt-5", temperature=0.7, max_tokens=3000
    )

    def generate_content(iteration: int, feedback_history: List[str]) -> str:
        user_message = f"""
Please convert each complex block identifier into actual system prompt content while maintaining the exact same structure.

Here is the complex block structure to populate:

{complex_block}

Remember to:
- Replace each [identifier] with relevant content + [complexity_block]
- Keep all parenthetical content unchanged
- Tailor content to the context
- Make content actionable and clear
- Maintain natural flow
"""

        # Add feedback history if exists
        if feedback_history:
            user_message += ("\n\nPrevious feedback to incorporate:\n" +
                             "\n".join(feedback_history))

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message.strip()}
        ]

        return content_model.generate(messages)

    return interactive_feedback_loop(
        generate_content,
        max_iterations=5,
        task_name="Populating Content From Complex Block"
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

    system_prompt = """You are a system prompt enhancer that adds system setting information to the FIRST CONTEXT_INFORMATION block.

Your task:
1. Analyze the provided context and system settings to understand the user's environment
2. Generate 2-5 pieces of relevant system setting information
3. Add this information ONLY to the FIRST CONTEXT_INFORMATION block you find in the structure
4. Leave all other blocks completely unchanged

Requirements:
- Add 2-5 pieces of system setting information to the FIRST CONTEXT_INFORMATION block only
- Generate system info dynamically based on context and settings
- Maintain the exact structure and format of the input
- Make additions feel natural and integrated
- Do NOT modify any other blocks

Instructions:
- Find the FIRST CONTEXT_INFORMATION block in the structure
- Add 2-5 pieces of relevant system setting information to that block only
- Generate system info that would be helpful for the specific context and settings
- Format: Add as natural extensions within the first CONTEXT_INFORMATION block
- Example: "[CONTEXT_INFORMATION] existing content (system: mobile device, storage: 64GB, network: WiFi)"

CRITICAL: Enhance ONLY the FIRST CONTEXT_INFORMATION block. Leave all others unchanged.

Focus on adding system setting information that's specifically relevant to the context."""

    model = create_model(model_id="gpt-4", temperature=0.7, max_tokens=3000)

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

        return model.generate(messages)

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
    coverage_pct = (len(found_blocks)/len(all_complex_blocks))*100
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
