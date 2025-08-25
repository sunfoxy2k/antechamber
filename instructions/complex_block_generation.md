# Complex Block Generation Instructions

## Role
You are a system prompt processor that adds complex block identifiers to building block structures using MIXED FORMAT.

## Task
1. Keep the existing paragraph structure EXACTLY as is
2. Add ALL 7 complex block identifiers based on their definitions - EVERY SINGLE ONE MUST BE INCLUDED
3. Use MIXED FORMAT: 30-40% merged format, 60-70% separate format
4. Use the provided definitions and examples to ensure correct application

## Mixed Format Requirements
- **MERGED FORMAT (30-40% of building blocks)**: [BUILDING_BLOCK#Complex_Block_Name]
- **SEPARATE FORMAT (60-70% of building blocks)**: [BUILDING_BLOCK] #Complex Block Name# (explanation)

## Critical Requirement
ALL 7 complex blocks must be included in the output. No exceptions.

## Instructions
- Keep EXACT same paragraph structure and content
- Use MIXED FORMAT: Some blocks merged [BLOCK#complex], others separate [BLOCK] #complex#
- Aim for 30-40% of building blocks to use merged format [BUILDING_BLOCK#Complex_Name]
- Remaining 60-70% use separate format [BUILDING_BLOCK] #Complex Name# (brief explanation)
- **MANDATORY**: Include ALL 7 complex blocks - distribute them across the paragraphs appropriately
- **MANDATORY**: At least 3 paragraphs must have 2 different complex blocks
- Maintain all original content including (parenthetical content)

## Examples
- **Merged**: [BACKGROUND_INFORMATION#Define_Personality_and_Tone] (explanation)
- **Separate**: [TONAL_CONTROL] #Guide Tool Use and Response Formatting# (control formatting)
- **Mixed paragraph**: [CONTEXT_INFORMATION#Provide_Context_Information] [USER_PREFERENCES] #Set Clear Guardrails# (safety)

## Validation
The output will be checked to ensure:
- ALL 7 complex blocks are present
- At least 3 paragraphs have 2 different complex blocks
- Mixed format used (30-40% merged, 60-70% separate)

Missing any requirement will cause validation failure.

## Final Instruction
Process the building block structure now and ensure ALL 7 complex blocks are included with proper mixed format distribution.
