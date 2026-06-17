# Upstreams And Attribution

This file records the upstream projects inspected before implementation. The initial Limes scaffold does not copy source files from these projects. It reuses high-level ideas only: fixed-budget experiments, an editable experiment target, scalar metric comparison, append-only results, and Mac-friendly backend detection.

## Summary

| Upstream | URL | Inspected SHA | License finding | Reused in this repo |
|---|---|---:|---|---|
| Karpathy AutoResearch | https://github.com/karpathy/autoresearch | `228791fb499afffb54b46200aca536f79142f117` | README has a `License` section stating `MIT`; no standalone license file was present in the inspected checkout and GitHub API did not detect a license. | Concepts only: fixed-time loop, mutable training file idea, `val_bpb` as a comparable metric, agent protocol framing. No source code copied. |
| autoresearch-macos | https://github.com/miolini/autoresearch-macos | `537c6e6d0ecf7d28f9d70ce20bb05d8c7ed9cfce` | README has a `License` section stating `MIT`; no standalone license file was present in the inspected checkout and GitHub API did not detect a license. | Concepts only: macOS/MPS support goals, CPU fallback, avoiding hard requirements on CUDA-only paths. No source code copied. |
| autoresearch-mlx | https://github.com/trevin-creator/autoresearch-mlx | `ba6ebf6d3594c0f33dbf753fafa8cad96f41c6d8` | MIT License file present. Copyright notices name Andrej Karpathy and Trevin Peterson. GitHub API detected MIT. | Concepts only: optional MLX direction, JSON/TSV-style experiment history, Apple Silicon fixed-budget interpretation. No source code copied. |
| andyluo7 AutoResearch | https://github.com/andyluo7/autoresearch | `c2c12b281c275850705031837e0f5712488a3982` | README has a `License` section stating `MIT`; no standalone license file was present in the inspected checkout and GitHub API did not detect a license. | Concepts only: portability interest beyond NVIDIA/CUDA. No source code copied. |

## License Compatibility Decision

The initial repository is implemented from scratch under the Limes Labs MIT license. Because three inspected repositories lacked a standalone license file and GitHub did not detect their license metadata, this branch does not import their code even where README text says MIT. Future direct code import should require:

1. A specific file-level reuse plan.
2. A checked license file or explicit upstream clarification.
3. Preserved copyright and MIT notice text where required.
4. A note in this file naming each imported file and local destination.

## Related Research Context

- [AutoResearch-RL: Perpetual Self-Evaluating Reinforcement Learning Agents for Autonomous Neural Architecture Discovery](https://arxiv.org/abs/2603.07300). arXiv currently marks this submission as withdrawn by arXiv Admin; cite cautiously.
- [Bilevel Autoresearch: Meta-Autoresearching Itself](https://arxiv.org/abs/2603.23420). Useful for thinking about outer loops that improve the inner search mechanism, not only the target experiment.
- [Can LLMs Beat Classical Hyperparameter Optimization Algorithms? A Study on autoresearch](https://arxiv.org/abs/2603.24647). Useful caution: classical HPO can outperform pure LLM agents in constrained spaces, while hybrids can combine optimizer state with LLM priors.

## Inspection Commands

```bash
gh api repos/karpathy/autoresearch --jq '{full_name,default_branch,license:.license.spdx_id,license_name:.license.name}'
gh api repos/miolini/autoresearch-macos --jq '{full_name,default_branch,license:.license.spdx_id,license_name:.license.name}'
gh api repos/trevin-creator/autoresearch-mlx --jq '{full_name,default_branch,license:.license.spdx_id,license_name:.license.name}'
gh api repos/andyluo7/autoresearch --jq '{full_name,default_branch,license:.license.spdx_id,license_name:.license.name}'
git ls-remote https://github.com/karpathy/autoresearch.git HEAD refs/heads/master refs/heads/main
git ls-remote https://github.com/miolini/autoresearch-macos.git HEAD refs/heads/master refs/heads/main
git ls-remote https://github.com/trevin-creator/autoresearch-mlx.git HEAD refs/heads/master refs/heads/main
git ls-remote https://github.com/andyluo7/autoresearch.git HEAD refs/heads/master refs/heads/main
```
