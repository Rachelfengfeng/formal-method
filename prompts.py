prompt_lean2nl = r"""
Task:
You are given a formal mathematical proof written as a Lean4 code, provided in a "<proof>" tag.
Translate it into an informal proof written in natural language.

<proof>
{proof}
</proof>

Instructions:
1. If the formal proof contains several steps, try to do the translation step by step.
2. Make sure that the reasoning in your translated proof is self-contained and matches the formal proof, step by step.
3. The provided formal proof may contain comments which you may leverage.
However, the existing comments alone may not be complete,
and thus you should consider both comments and other parts of the code in the formal proof.
4. Directly give the translated result. Do not output any thing extra.
"""

prompt_lean2nl_without_comments = r"""
Task:
You are given a formal mathematical proof written as a Lean4 code, provided in a "<proof>" tag.
Translate it into an informal proof written in natural language.

<proof>
{proof}
</proof>

Instructions:
1. If the formal proof contains several steps, try to do the translation step by step.
2. Make sure that the reasoning in your translated proof is self-contained and matches the formal proof, step by step.
3. Directly give the translated result. Do not output any thing extra.
"""

prompt_herald = r"""
<informal_theorem>
{informal_theorem}
</informal_theorem>

<formal_theorem>
{formal_theorem}
</formal_theorem>

<informal_proof>
{informal_proof}
</informal_proof>
"""

prompt_informal2formal = r"""Given an informal proof written in natural language, translate it into a formal proof in Lean4.

<informal_proof>
{informal_proof}
</informal_proof>
"""

prompt_informal2formal_with_problem = r"""For a math proof problem (provided in the "<problem>" tag), given an informal proof written in natural language (provided in the "<proof>" tag), translate it into a formal proof in Lean4.

<problem>
{problem}
</problem>

<proof>
{proof}
</proof>
"""

prompt_informal_problem_only = r"""For a math proof problem (provided in the "<problem>" tag), write a formal proof in Lean4.

<problem>
{problem}
</problem>
"""

# Removed '\\n<|EOT|>\\n' and "{{'### Response:\\n'}}\n"
# chat_template_partial = "{%- set found_item = false -%}\n{%- for message in messages -%}\n    {%- if message['role'] == 'system' -%}\n        {%- set found_item = true -%}\n    {%- endif -%}\n{%- endfor -%}\n{%- if not found_item -%}\n{{'You are a helpful AI assistant.\\n'}}\n{%- endif %}\n{%- for message in messages %}\n    {%- if message['role'] == 'system' %}\n{{ message['content'] }}\n    {%- else %}\n        {%- if message['role'] == 'user' %}\n{{'### Instruction:\\n' + message['content'] + '\\n'}}\n        {%- else %}\n{{'### Response:\\n' + message['content']}}\n        {%- endif %}\n    {%- endif %}\n{%- endfor %}"
chat_template_partial = "{% for message in messages %}{%- if message['role'] == 'user' %}{{'<|im_start|>user\n' + message['content'] + '<|im_end|>' + '\n'}}{%- else %}{{'<|im_start|>assistant\n' + message['content']}}{%- endif %}{% endfor %}{% if end_generation %}{{ '<|im_end|>' + '\n' }}{% endif %}"

prompt_solve_informal = r"""
Solve the given math problem and provide your reasoning step-by-step.

{informal_problem}
"""

prompt_solve_informal_gpt41 = r"""
Solve the given math problem.
Please provide a proof step by step.
Do not output your thinking that is not an essential part of the proof.
Do not include steps that you eventually discard.

{informal_problem}
"""


prompt_translate_statement = """
Given a problem written in natural language, translate it into a formal statement in Lean4.

The problem written in the informal natural language is in the "<informal_problem>" tag.

Your output should be a Lean4 code which is the formal statement (followed by “by sorry”) that can pass Lean4 compilation.

Directly output the code without anything else. Begin your output by "theorem" (no need to add headers).

Please refer to examples below.
In the formal statement, you should declare any variables as parameters, not as ∀ quantifiers.
Your formal statement should meaningfully cover the informal problem, instead of simply putting a final result.

Good: theorem sample_theorem (a b c : ℝ) (h : a / (b + c) = 1) : a ^ 2 + b ^ 2 + c ^ 2 ≥ (6 / 5) * (a * b + b * c + c * a) := by sorry
Bad: theorem sample_theorem : ∀ (a b c : ℝ), a / (b + c) = 1 → a ^ 2 + b ^ 2 + c ^ 2 ≥ (6 / 5) * (a * b + b * c + c * a) := by sorry
Bad: theorem sample_theorem : True := by sorry
Bad: theorem sample_theorem : 1 + 2 = 3 := by sorry

<informal_problem>
{informal_problem}
</informal_problem>
"""

prompt_translate_sketch_only = """
Given an informal proof written in natural language, translate it into a formal proof in Lean4.

The problem written in the informal natural language is in the "<informal_problem>" tag.
The problem written in the formal Lean4 language is in the "<formal_problem>" tag.
The proof written in the informal natural language is in the "<informal_proof>" tag.

Your output should be a Lean4 code which is the formal proof that can pass Lean4 compilation.
Directly output the code without anything else.
The formal proof in your output should match the provided informal proof, step by step.

Expected format for each step:
1. First, add a comment explaining what the step is doing.
2. Define a `have` statement to describe what is being achieved in this step.
3. For now, no need to write detailed reasoning step. Simply use `by sorry` for each have.

Before the "have-by" steps in the formal proof, there should not be any extra step, such as "intro".
You should avoid using the "intro" tactic.

<informal_problem>
{informal_problem}
</informal_problem>

<formal_problem>
{formal_problem}
</formal_problem>

<informal_proof>
{informal_proof}
</informal_proof>
"""

prompt_translate_sketch_and_partial_proof = """
Given an informal proof written in natural language, translate it into a formal proof in Lean4.

The problem written in the informal natural language is in the "<informal_problem>" tag.
The problem written in the formal Lean4 language is in the "<formal_problem>" tag.
The proof written in the informal natural language is in the "<informal_proof>" tag.

Your output should be a Lean4 code which is the formal proof that can pass Lean4 compilation.
Directly output the code without anything else.
The formal proof in your output should match the provided informal proof, step by step.

Expected format for each step:
1. First, add a comment explaining what the step is doing.
2. Define a `have` statement to describe what is being achieved in this step.
3. Under the `have` statement, try to include the proof if and only if it exists in the given informal proof. In case that the corresponding proof for the step is missing or incomplete in the given informal proof, you may leverage the "sorry" tactic to indicate that. Overall, you should try to make the step in the formal proof a faithful translation of the corresponding step in the informal proof, without any addition or deletion.

<informal_problem>
{informal_problem}
</informal_problem>

<formal_problem>
{formal_problem}
</formal_problem>

<informal_proof>
{informal_proof}
</informal_proof>
"""

prompt_translate = {
    "v1": prompt_translate_sketch_only,
    "v2": prompt_translate_sketch_and_partial_proof,
}

prompt_header = r"""
Start your output with the header shown in the "<header>" tag:
<header>
{header}
</header>
"""

header_default = r"""
import Mathlib
import Aesop

open BigOperators Real Nat Topology Rat
"""

# A simple version for training.
# A longer one is at https://github.com/ucr-rai/formal_verify_step-by-step/blob/14ac0cd2f04b0415570c5c7d0095f75ee7439002/math500lean/rf_prompt_answer_replacement_v2.txt
prompt_replacement_function = r"""
You are given an informal problem statement (in the "<informal_problem>" tag) in natural language.
You are also given a formal problem statement (in the "<formal_problem>" tag) in Lean 4, which aims to prove that a certain answer (in the "<answer>" tag) is correct for the original problem.
Your task is to write a Python function that takes any new answer and returns a new formal problem statement, with the answer in the problem statement replaced by the new answer, while keeping the rest of the problem statement unchanged.
The function should start with `def fill_answer(answer: str) -> str:`.

<informal_problem>
{informal_problem}
</informal_problem>

<formal_problem>
{formal_problem}
</formal_problem>

<answer>
{answer}
</answer>
"""
