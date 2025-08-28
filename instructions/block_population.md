# Block Population Instructions

## Objective
Convert structured block format into a natural, flowing system prompt written in plain English. 


## Core Task
Transform this format: `[BLOCK_NAME] (explanation) #complex_block# (explanation) __unparaphrased ideas__`
Into natural paragraphs that directly instruct the AI system.

## Writing Style
- **Voice**: Use "You" to address the AI system directly
- **Tone**: Clear, direct, professional instructions
- **Format**: Natural paragraphs, no bullet points or lists
- **Language**: Simple, concrete words - avoid jargon
- **Avoid repetition**: Don't repeat the same concepts, phrases, or rephrasing of ideas
- **No feature lists**: Don't list capabilities, features, or characteristics
- **No adjective lists**: Avoid listing multiple adjectives like "extroverted, considerate, helpful"
- **No block references**: Never mention block names like "[CONTEXT_INFORMATION]" or "#Define_Personality_and_Tone#"
- **No tool references**: Never mention specific tools from user context conversation_flow

## Transformation Rules
1. **Building Blocks** `[BLOCK_NAME]` → Convert to specific instructions based on the block's purpose
2. **Complex Blocks** `#complex_name#` → Convert to actionable guidelines based on the definition
3. **Content in Double Underscores** `__content__` → remove __ and naturually link the content to the previous and next sentences. You may make minor adjustments for natural flow, but DO NOT change the core ideas, concepts, or meaning contained within the double underscores
4. **Required Text** → Include the SYSTEM_PROMPT_MUST content word-for-word somewhere in the output


## Key Requirements
- Write as direct instructions to the AI system
- Be specific about tool usage (name exact tools and triggers)
- Create smooth paragraph flow between different block types
- Maintain all original meaning while making it conversational
- **CRITICAL**: Preserve the exact wording and meaning of content within `__double underscores__` - only make minimal changes for grammatical flow
- **User Reference**: Mention the user's name only once, then refer to them as "the user" throughout the rest of the prompt
- Do not quote or paraphrase what the user is currently doing (avoid referencing "what_they_are_doing_for_current_task")
- Never use "we" or "us" - keep it objective
- Avoid repetitive phrasing, redundant concepts, and rephrasing the same ideas
- Don't enumerate features, capabilities, or characteristics in lists
- Replace adjective lists with single, precise descriptors
- Transform block names into natural instructions without mentioning the block structure
- Never reference tools mentioned in user context conversation_flow
- Use clear, straightforward sentences without unnecessary complexity

## Quality Check
The final output should read like a professional system prompt that any AI system could follow immediately, with clear actionable instructions in natural English.

