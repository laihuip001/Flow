---
description: Load a prompt module by ID into the current session
---

# /load Workflow

Load a prompt module from the Prompt Library into the current conversation context.

## Usage

```
/load C-4-5
/load A-9
/load Q-1
```

## Steps

1. **Identify module ID** from user input (e.g., `C-4-5`, `A-9`, `Q-1`)

2. **Map ID to file path**:
   - `C-1-2` → `dev-rules/prompts/modules/C1C2-adversarial.md`
   - `C-3` → `dev-rules/prompts/modules/C3-structural_audit.md`
   - `C-4-5` → `dev-rules/prompts/modules/C4C5-code.md`
   - `C-6-7` → `dev-rules/prompts/modules/C6C7-prompt.md`
   - `Q-1` → `dev-rules/prompts/modules/Q1-feynman_filter.md`
   - `Q-2` → `dev-rules/prompts/modules/Q2-second_order_thinking.md`
   - `Q-3` → `dev-rules/prompts/modules/Q3-occams_razor.md`
   - `Q-4` → `dev-rules/prompts/modules/Q4-aesthetic_audit.md`
   - `A-2` → `dev-rules/prompts/modules/A2-lateral_thinking.md`
   - `A-3` → `dev-rules/prompts/modules/A3-bias_scanner.md`
   - `A-7` → `dev-rules/prompts/modules/A7-context_articulation.md`
   - `A-8` → `dev-rules/prompts/modules/A8-morphological_matrix.md`
   - `A-9` → `dev-rules/prompts/modules/A9-first_principles.md`
   - `B-3` → `dev-rules/prompts/modules/B3-context_cartography.md`
   - `E-1` → `dev-rules/prompts/modules/E1-tactical_roadmap.md`
   - `I-1` → `dev-rules/prompts/modules/I1-context_integration.md`
   - `M-1` → `dev-rules/prompts/modules/M1-agent_command_compiler.md`
   - `R-1` → `dev-rules/prompts/modules/R1-reverse_engineering.md`
   - `X-1-2` → `dev-rules/prompts/modules/X1X2-divergence_convergence.md`
   - `D-1` → `dev-rules/prompts/modules/D1-design_review.md`
   - `Rec` → `dev-rules/prompts/modules/recommender.md`

3. **Read the module file** using `view_file` tool

4. **Apply the module** against the previous output or specified context

5. **Output** the result in the format specified by the module

## Example

```
User: /load C-4-5
Agent: [Reads C4C5-code.md, switches to Code Audit mode]
Agent: Please provide the code to audit.

User: <paste code>
Agent: ## Code Audit Report
       ...
```

## Notes

- Modules with dual modes (audit/fix) will prompt for mode selection
- Use `/load C-4-5 audit` or `/load C-4-5 fix` to specify mode directly
