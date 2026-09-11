---
name: change-impact-analysis
description: Analyze a Git diff or commit, trace direct and indirect dependencies, and propose an evidence-based regression scope. Use for code change impact analysis; do not use it to declare bugs or replace business judgment and test execution.
---

# Change Impact Analysis

Turn a concrete code change into a reviewable regression recommendation. Keep static-analysis conclusions separate from facts confirmed by execution.

## Inputs and boundaries

- Confirm the repository instructions, requested diff range, environment, and allowed actions before analysis.
- Prefer an existing working-tree, staged, commit, or PR diff. If a temporary controlled diff is truly necessary, label it as practice input and remove it after verification.
- Preserve unrelated local changes. Do not commit, push, edit a PR, or change business code unless the user separately asks for that action.
- Treat AI output as risk candidates and regression advice. Only a tester can confirm business impact or a bug after checking requirements, code, and observed results.

## Workflow

1. **Read the diff.** Use the narrowest relevant command, such as `git diff`, `git diff --cached`, or `git show <commit>`. Include `--name-status`, `--stat`, and `--find-renames` when paths may have moved.
2. **Identify the change unit.** Record changed files, symbols, configuration keys, signatures, return shapes, side effects, and path-only changes. A zero-line rename can still change framework discovery or import behavior.
3. **Search references.** Use `rg` for imports, calls, fixture names, test parameters, configuration keys, markers, and filenames. Do not search only explicit Python imports: frameworks such as Pytest can create implicit dependencies.
4. **Trace dependencies.** Follow direct consumers into fixtures, helpers, clients, Page Objects, data factories, configuration, and cleanup paths. Stop where evidence no longer supports a dependency.
5. **Map tests by layer.** Separate directly affected tests, indirectly affected tests, adjacent safety checks, and tests that are out of scope. Explain every inclusion and exclusion.
6. **Propose the minimum reasonable regression set.** Cover each changed behavior and each proven dependency path. Add broader collection or integration checks when the change can affect test discovery, shared setup, environment loading, or cleanup.
7. **Ask for human confirmation.** Surface assumptions, business decisions, environment requirements, destructive cleanup, and risks that static analysis cannot resolve.
8. **Execute the confirmed tests.** Record the exact command, collected count, pass/fail/error/skip counts, environment, and relevant cleanup. Distinguish product failures from test-infrastructure failures.
9. **Compare prediction with evidence.** State whether execution matched the proposed impact. If it did not, update the dependency map and recommendation rather than forcing the original conclusion.

## Required result

Answer these points with file, symbol, diff, or command evidence:

1. What changed?
2. Who references it directly?
3. Which tests are affected indirectly, and through what chain?
4. Which layers are not affected, and why?
5. What is the minimum reasonable regression set?
6. Which risks cannot static analysis confirm?
7. Which tests were actually executed, in which environment, and with what result?
8. Did the analysis match the observed result?

End with the tester's confirmed decision and any remaining uncertainty. Never phrase a suggested test range as an automatically decided final range.
