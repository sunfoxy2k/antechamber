# Block Population Instructions

## Objective
Convert structured block format into a natural, flowing system prompt written in plain English.

## Core Task
Transform this format: `[BLOCK_NAME] (explanation) #complex_block# (explanation)`
Into natural paragraphs that directly instruct the AI system.

## Writing Style
- **Voice**: Use "You" to address the AI system directly
- **Tone**: Clear, direct, professional instructions
- **Format**: Natural paragraphs, no bullet points or lists
- **Language**: Simple, concrete words - avoid jargon

## Transformation Rules
1. **Building Blocks** `[BLOCK_NAME]` → Convert to specific instructions based on the block's purpose
2. **Complex Blocks** `#complex_name#` → Convert to actionable guidelines based on the definition
3. **Required Text** → Include the SYSTEM_PROMPT_MUST content word-for-word somewhere in the output

## Key Requirements
- Write as direct instructions to the AI system
- Be specific about tool usage (name exact tools and triggers)
- Create smooth paragraph flow between different block types
- Maintain all original meaning while making it conversational
- Never use "we" or "us" - keep it objective

## Quality Check
The final output should read like a professional system prompt that any AI system could follow immediately, with clear actionable instructions in natural English.

