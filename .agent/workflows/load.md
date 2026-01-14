---
description: Load a prompt module by ID into the current session
---

# /load Workflow

Load a prompt module from the Prompt Library into the current conversation context.

## Usage

```text
/load C-4-5        # By ID
/load おべっかの無い評価   # By Japanese filename
/load vibe         # By keyword search
```

## Steps

1. **Identify module** from user input (ID, filename, or keyword)

2. **Resolution Order**:
   - **Step 2a**: Check ID map (below)
   - **Step 2b**: If not found, search for `*.md` file matching input in:
     `c:/Users/laihuip001/dev/dev-rules/prompts/modules/`

3. **ID to File Path Map (Core Modules)**:
   - `C-1-2` → `C1C2-adversarial.md`
   - `C-3` → `C3-structural_audit.md`
   - `C-4-5` → `C4C5-code.md`
   - `C-6-7` → `C6C7-prompt.md`
   - `Q-1` → `Q1-feynman_filter.md`
   - `Q-2` → `Q2-second_order_thinking.md`
   - `Q-3` → `Q3-occams_razor.md`
   - `Q-4` → `Q4-aesthetic_audit.md`
   - `A-2` → `A2-lateral_thinking.md`
   - `A-3` → `A3-bias_scanner.md`
   - `A-7` → `A7-context_articulation.md`
   - `A-8` → `A8-morphological_matrix.md`
   - `A-9` → `A9-first_principles.md`
   - `B-3` → `B3-context_cartography.md`
   - `E-1` → `E1-tactical_roadmap.md`
   - `I-1` → `I1-context_integration.md`
   - `M-1` → `M1-agent_command_compiler.md`
   - `R-1` → `R1-reverse_engineering.md`
   - `X-1-2` → `X1X2-divergence_convergence.md`
   - `D-1` → `D1-design_review.md`
   - `P-1` → `P1-vibe_audit.md`
   - `Rec` → `recommender.md`
   - `EP` → `EP-execution_prime.md`
   - `GDR` → `GDR-knowledge_converter.md`

4. **Japanese Modules (Integrated)**:
   - `おべっかの無い評価` - Brutally honest evaluation
   - `エレガンススマート監査` - Elegance/smart audit
   - `オッカムのカミソリ` - Occam's Razor
   - `コンテキストの言語化` - Context articulation
   - `コンテキスト構造化` - Context structuring
   - `コーディング仕様書コンパイル` - Coding spec compilation
   - `コード外科手術凹` - Code surgery (fix)
   - `コード監査凸` - Code audit
   - `システム・ダイナミクス予想` - System dynamics prediction
   - `システム構造監査` - System structure audit
   - `プロンプト外科手術凹` - Prompt surgery (fix)
   - `プロンプト構造監査凸` - Prompt structure audit
   - `リバースエンジニアリング` - Reverse engineering
   - `七世代先の視点` - Seven generations ahead
   - `仮想ユーザー座談会` - Virtual user discussion
   - `単純性原理と平易な説明` - Simplicity and plain explanation
   - `回答の解像度向上` - Answer resolution improvement
   - `外科的再構築凹` - Surgical reconstruction
   - `外部文脈の結合` - External context integration
   - `多角的ラテラル・シンキング` - Lateral thinking
   - `形態素解析マトリクス` - Morphological matrix
   - `成功の解体新書` - Success deconstruction
   - `敵対的レビュー凸` - Adversarial review
   - `未踏の改善点` - Unexplored improvements
   - `現実への接地` - Grounding to reality
   - `発散と収束` - Divergence and convergence
   - `第一原理思考` - First principles thinking
   - `経験の法則化` - Experience systematization
   - `自律思考` - Autonomous thinking
   - `論理的背景の補強` - Logical background reinforcement
   - `WBSスケジューリング` - WBS scheduling

5. **Read the module file** using `view_file` tool

6. **Apply the module** against the previous output or specified context

7. **Output** the result in the format specified by the module

## Example

```text
User: /load おべっかの無い評価
Agent: [Reads おべっかの無い評価.md, applies brutal evaluation mode]

User: /load C-4-5 audit
Agent: [Reads C4C5-code.md, switches to Code Audit mode]
```

## Notes

- Modules with dual modes (audit/fix) will prompt for mode selection
- Use `/load <module> audit` or `/load <module> fix` to specify mode directly
- All modules are located in: `c:/Users/laihuip001/dev/dev-rules/prompts/modules/`
