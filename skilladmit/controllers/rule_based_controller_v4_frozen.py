from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ACTIONS = [
    "discard",
    "store_as_memory",
    "distill_into_skill",
    "promote_to_rule",
    "defer",
]


@dataclass
class AdmissionDecision:
    prediction: str
    scores: dict[str, float]
    reason: str


class RuleBasedSkillAdmitController:
    """A small deterministic controller for the seed benchmark.

    This is not the final research method. It is the first executable baseline
    that turns feature intuitions into an admission decision.
    """

    def predict(self, sample: dict[str, Any]) -> AdmissionDecision:
        text = self._sample_text(sample)

        context_specificity = self._context_specificity(text)
        transferability = self._transferability(text)
        stability = self._stability(sample)
        overgeneralization_risk = self._overgeneralization_risk(text)
        rule_generality = self._rule_generality(sample)
        evidence_sufficiency = self._evidence_sufficiency(sample)
        harmful_skill_risk = self._harmful_skill_risk(sample)
        guardrail_rule_signal = self._guardrail_rule_signal(sample, text)
        insufficient_evidence = self._insufficient_evidence_signal(sample, text)
        memory_specific_signal = self._memory_specific_signal(sample, text)
        runner_noise_signal = self._runner_noise_signal(sample, text)

        scores = {
            "discard": 0.0,
            "store_as_memory": 0.0,
            "distill_into_skill": 0.0,
            "promote_to_rule": 0.0,
            "defer": 0.0,
        }

        scores["store_as_memory"] = (
            0.55 * context_specificity
            + 0.20 * evidence_sufficiency
            - 0.20 * transferability
            + 1.05 * memory_specific_signal
            - 0.35 * insufficient_evidence
            - 0.30 * stability * transferability
        )

        scores["distill_into_skill"] = (
            0.42 * transferability
            + 0.30 * stability
            + 0.25 * evidence_sufficiency
            - 0.35 * overgeneralization_risk
            - 0.10 * context_specificity
            - 0.60 * harmful_skill_risk
            - 0.35 * insufficient_evidence
            - 0.45 * guardrail_rule_signal
            - 0.50 * memory_specific_signal
        )

        scores["promote_to_rule"] = (
            0.45 * rule_generality
            + 0.20 * transferability
            - 0.15 * context_specificity
            + 0.20 * stability
            + 0.85 * guardrail_rule_signal
            - 0.70 * harmful_skill_risk
            - 0.30 * memory_specific_signal
        )

        scores["defer"] = (
            0.45 * overgeneralization_risk
            + 0.35 * (1.0 - evidence_sufficiency)
            + 0.25 * self._needs_negative_validation(text)
            + 0.55 * insufficient_evidence
            - 0.70 * memory_specific_signal
            - 0.40 * runner_noise_signal
            - 0.55 * harmful_skill_risk
        )

        scores["discard"] = (
            0.30 * self._noise_likelihood(text)
            + 0.20 * (1.0 - transferability)
            + 0.20 * (1.0 - evidence_sufficiency)
            + 1.25 * harmful_skill_risk
            + 0.75 * runner_noise_signal
            - 0.50 * guardrail_rule_signal
            - 0.55 * insufficient_evidence
        )

        prediction = max(scores, key=scores.get)

        reason = (
            f"context_specificity={context_specificity:.2f}, "
            f"transferability={transferability:.2f}, "
            f"stability={stability:.2f}, "
            f"risk={overgeneralization_risk:.2f}, "
            f"rule_generality={rule_generality:.2f}, "
            f"evidence={evidence_sufficiency:.2f}, "
            f"harmful={harmful_skill_risk:.2f}, "
            f"guardrail={guardrail_rule_signal:.2f}, "
            f"insufficient={insufficient_evidence:.2f}, "
            f"memory_specific={memory_specific_signal:.2f}, "
            f"runner_noise={runner_noise_signal:.2f}"
        )

        return AdmissionDecision(prediction=prediction, scores=scores, reason=reason)

    def _sample_text(self, sample: dict[str, Any]) -> str:
        parts = [
            sample.get("cluster_name", ""),
            sample.get("candidate_memory", ""),
            sample.get("candidate_rule", ""),
        ]

        skill = sample.get("candidate_skill", {})
        parts.append(skill.get("name", ""))

        for key in ["trigger", "steps", "limitations"]:
            value = skill.get(key, [])
            if isinstance(value, list):
                parts.extend(str(v) for v in value)
            else:
                parts.append(str(value))

        for item in sample.get("experience_cluster", []):
            parts.extend(str(item.get(k, "")) for k in ["observation", "diagnosis", "fix_pattern", "risk"])

        return "\n".join(parts).lower()

    def _context_specificity(self, text: str) -> float:
        markers = [
            "this task group",
            "specific project",
            "current project",
            "port",
            "path",
            "cwd",
            "working directory",
            "repo",
            "app directory",
        ]
        return self._marker_score(text, markers)

    def _transferability(self, text: str) -> float:
        markers = [
            "diagnose",
            "check",
            "inspect",
            "before",
            "procedure",
            "steps",
            "reusable",
            "module",
            "package",
            "import",
            "load",
            "validate",
            "parse",
            "schema",
            "request",
            "response",
            "streaming",
            "timeout",
            "proxy",
            "configuration",
            "config",
            "rate limit",
            "backoff",
            "json",
            "env",
        ]
        return self._marker_score(text, markers)

    def _stability(self, sample: dict[str, Any]) -> float:
        cluster_size = len(sample.get("task_ids", []))
        if cluster_size >= 4:
            return 1.0
        if cluster_size >= 3:
            return 0.8
        if cluster_size >= 2:
            return 0.5
        return 0.2

    def _overgeneralization_risk(self, text: str) -> float:
        markers = [
            "every modulenotfounderror",
            "blind",
            "blindly",
            "install",
            "pip install",
            "overgeneralize",
            "negative transfer",
            "do not assume every",
            "risky",
            "risk",
        ]
        return self._marker_score(text, markers)

    def _rule_generality(self, sample: dict[str, Any]) -> float:
        rule = sample.get("candidate_rule", "").lower()
        markers = ["before", "do not", "first check", "confirm", "rather than"]
        return self._marker_score(rule, markers)

    def _evidence_sufficiency(self, sample: dict[str, Any]) -> float:
        cluster_size = len(sample.get("task_ids", []))
        has_skill_steps = bool(sample.get("candidate_skill", {}).get("steps"))
        if cluster_size >= 4 and has_skill_steps:
            return 0.9
        if cluster_size >= 3:
            return 0.7
        return 0.4

    def _needs_negative_validation(self, text: str) -> float:
        markers = [
            "third-party dependency",
            "external dependency",
            "install missing",
            "overgeneralize",
            "not assume every",
        ]
        return self._marker_score(text, markers)

    def _harmful_skill_risk(self, sample: dict[str, Any]) -> float:
        """Estimate whether the candidate *proposes* a harmful repair.

        This intentionally ignores candidate_skill.limitations because a good
        skill often says "do not use sys.path hacks" or "do not blindly install
        packages" in its limitations. Counting those guardrails as harmful
        actions would punish well-scoped skills.
        """
        skill = sample.get("candidate_skill", {})
        parts = [
            sample.get("cluster_name", ""),
            sample.get("candidate_rule", ""),
            str(skill.get("name", "")),
            str(skill.get("risk", "")),
        ]

        for key in ["trigger", "steps"]:
            value = skill.get(key, [])
            if isinstance(value, list):
                parts.extend(str(v) for v in value)
            else:
                parts.append(str(value))

        text = "\n".join(parts).lower()
        protective_phrases = [
            "do not edit tests",
            "do not modify tests",
            "do not edit tests or verifier",
            "do not modify tests or verifier",
            "do not edit verifier",
            "do not admit",
            "do not store",
            "do not use",
            "avoid sys.path",
            "avoid sys.path hacks",
            "never print full api keys",
            "never print full key values",
            "never print full",
            "only report presence or redacted values",
            "print non-secret",
        ]
        for phrase in protective_phrases:
            text = text.replace(phrase, "")

        severe_markers = [
            "actively harmful",
            "delete the failing test",
            "delete failing tests",
            "remove the failing test",
            "return true",
            "constant successful value",
            "return constant success",
            "fakes success",
            "fake success",
            "fabricates correctness",
            "fabricates results",
            "chmod -r 777",
            "world-writable",
            "return an empty dict",
            "return empty data",
            "turn off schema validation",
            "disable the validator",
            "bypass validation",
            "delete the database",
            "delete persistent state",
            "catch exception and continue",
            "catch exception",
            "except exception",
            "lower the passing threshold",
            "lower metrics",
            "print all secrets",
            "print the full .env",
        ]
        if any(marker in text for marker in severe_markers):
            return 1.0

        markers = [
            "actively harmful",
            "bad skill",
            "brittle workaround",
            "negative-transfer",
            "negative transfer",
            "blindly install",
            "install a package with the same name",
            "any modulenotfounderror",
            "omits local-module",
            "causes negative transfer",
            "sys.path hack",
            "sys.path hacks",
            "add more directories to sys.path",
            "append the repository root",
            "append the repository root and all subdirectories",
            "mask real packaging bugs",
            "hides root causes",
            "hides the real issue",
            "edit tests",
            "patch tests",
            "change expected values",
            "violates benchmark semantics",
            "destroys the verifier",
            "attacks the verifier",
            "invalidates verification",
            "catch importerror",
            "try/except importerror",
            "suppress import errors",
            "suppressing import errors",
            "does not fix the underlying import relation",
            "undefined behavior",
            "hides package bugs",
            "skip the verifier",
            "without verifier",
            "mark success",
            "does not need verifier",
            "unverified repairs",
            "modify verifier.sh",
            "replace pytest with true",
            "change verifier.sh",
            "exit successfully",
            "delete files",
            "delete the file",
            "remove it from the project",
            "random code edits",
            "edit nearby lines randomly",
            "catch-all exception",
            "except exception",
            "catch it and return a placeholder",
            "return a default value",
            "suppress exceptions",
            "suppress exceptions to pass tests",
            "verify=false",
            "verify = false",
            "disable ssl verification",
            "disabling tls verification",
            "disable certificate verification",
            "bypasses tls verification",
            "disable certificate verification globally",
            "hardcoded api",
            "hardcode",
            "hardcoding",
            "fake successful response",
            "fake success",
            "skip the api response",
            "return a fixed success object",
            "return hardcoded",
            "fabricates results",
            "print the full api key",
            "print full api keys",
            "print all secrets",
            "dumping .env",
            "leaks credentials",
            "retry immediately",
            "tight loop",
            "do not back off",
            "store the full raw trace",
            "store every raw",
            "always retrieve",
            "no filtering",
            "remove the failing test file",
            "replace the function body",
            "return true",
            "removes real behavior",
            "chmod -r 777",
            "world-writable",
            "empty dict",
            "empty data",
            "hides data loss",
            "disable the validator",
            "turn off schema validation",
            "malformed data",
            "global path injection",
            "pythonpath",
            "delete the database",
            "delete persistent state",
            "destroy user data",
            "catch exception",
            "use pass",
            "lower the passing threshold",
            "manipulates the metric",
        ]
        score = self._marker_score(text, markers)
        if "harmful operational pattern" in text or "high risk workaround" in text:
            score = max(score, 0.6)
        return score

    def _guardrail_rule_signal(self, sample: dict[str, Any], text: str) -> float:
        tags = set(sample.get("tags", []))
        skill = sample.get("candidate_skill", {})
        parts = [
            sample.get("cluster_name", ""),
            sample.get("candidate_memory", ""),
            sample.get("candidate_rule", ""),
            str(skill.get("name", "")),
        ]
        for key in ["trigger", "steps"]:
            value = skill.get(key, [])
            if isinstance(value, list):
                parts.extend(str(v) for v in value)
            else:
                parts.append(str(value))
        candidate_text = "\n".join(parts).lower()

        markers = [
            "guardrail",
            "before applying a generic",
            "constrain many",
            "cross_cluster",
            "broad guardrail",
            "determine whether",
            "global constraint",
            "general debugging constraint",
            "cross-skill control rule",
            "admission rule",
            "lifecycle rule",
            "experience-management rule",
            "general experience-management rule",
            "before admitting",
            "verify the repair outcome",
            "preconditions",
            "precondition",
            "retrieved skill",
            "do not modify",
            "do not edit",
            "do not change",
            "do not admit",
            "unless the task explicitly",
            "should constrain",
            "should apply",
            "separate infrastructure",
            "infrastructure events",
            "task-domain memory",
            "task-domain memory, skill, or rule",
            "never print",
            "redact secrets",
            "redacted values",
            "full api keys",
            "global safety constraint",
            "expected future utility",
            "future utility",
            "token cost",
            "validation cost",
            "budget",
            "budgeted",
            "admission should consider",
            "applies across memory, skill, and rule",
            "across memory, skill, and rule",
            "explicit triggers, scope, and limitations",
            "least destructive",
            "prefer the least destructive",
            "source evidence",
            "validation result",
            "admitted artifact",
            "provenance",
            "source trajectories",
            "record source",
            "record validation",
            "future debugging workflows",
        ]
        tag_score = 1.0 if "guardrail" in tags else 0.0
        return max(tag_score, self._marker_score(candidate_text, markers))

    def _insufficient_evidence_signal(self, sample: dict[str, Any], text: str) -> float:
        tags = set(sample.get("tags", []))
        cluster_size = len(sample.get("task_ids", []))
        markers = [
            "insufficient evidence",
            "one trajectory",
            "only one",
            "single",
            "not enough",
            "collect validation",
            "until validated",
            "based on only one",
            "needs more validation",
            "need more validation",
            "needs separate validation",
            "more formats need testing",
            "could be transient",
            "too vague",
            "underspecified",
            "under-specified",
            "does not define",
            "needs sharper decision boundary",
            "sharper decision boundary",
            "needs clearer decision boundary",
            "clearer decision boundary",
            "conflicting",
            "conflicts across providers",
            "different path bugs require different",
            "not enough evidence",
            "provider-specific",
            "different providers differ",
            "needs provider comparison",
            "provider comparison",
            "some endpoints work fine",
            "lacks precondition",
            "trial-and-error",
            "contradicts",
            "ambiguous",
            "may hide required dependency",
            "not enough projects observed",
            "small number of projects",
            "no tested backoff schedule",
            "no comparison with",
            "other networks may require",
            "hardware differs",
            "project size matters",
            "too heavy for small scripts",
            "deployment environments may",
            "decision boundary",
            "needs stronger preconditions",
            "optional versus required",
            "optional vs required",
            "small number of projects observed",
            "may be too heavy",
            "stale cache risk",
            "needs invalidation policy",
            "policy boundary is underspecified",
            "preference may change",
            "preference changed",
            "changed across phases",
            "current-turn",
            "context-dependent",
            "conflicts with later",
            "universal rule would be wrong",
        ]
        tag_score = 1.0 if "insufficient_evidence" in tags else 0.0
        size_score = 0.8 if cluster_size <= 1 else 0.0
        if cluster_size <= 1 and any(
            marker in text
            for marker in [
                "one project",
                "only one provider",
                "only one provider has been observed",
                "after multiple projects",
                "between memory, skill, or rule",
            ]
        ):
            size_score = 1.0
        return max(tag_score, size_score, self._marker_score(text, markers))

    def _memory_specific_signal(self, sample: dict[str, Any], text: str) -> float:
        tags = set(sample.get("tags", []))
        markers = [
            "specific task",
            "exact task",
            "exact file",
            "exact path",
            "not transferable",
            "bound to exact",
            "repo-specific",
            "environment-specific",
            "run configuration fact",
            "project-specific",
            "repository artifact location",
            "task metadata",
            "generated benchmark format",
            "conda env",
            "python 3.10",
            "model name",
            "current run",
            "synthetic",
            "synthetic absent module",
            "synthetic dependency",
            "module name starts",
            "naming convention",
            "benchmark-specific",
            "benchmark-specific metadata",
            "specific path",
            "specific file",
            "specific dependency",
            "not a general skill",
            "not a debugging skill",
            "not a general repair strategy",
            "not a transferable skill",
            "not a real dependency rule",
            "chosen to avoid environment pollution",
            "chosen to avoid installed packages",
            "record model name",
            "record command",
            "record synthetic name",
            "record it for reproducibility",
            "current api endpoint",
            "current provider",
            "current provider setting",
            "user's current",
            "current credentials",
            "store as project config",
            "this project currently",
            "latest llm traces",
            "current trajectory file",
            "repository state",
            "current real agent runner",
            "current runner",
            "local project state",
            "current benchmark metadata",
            "benchmark metadata",
            "counts will change",
            "dataset will change",
            "record sample counts",
            "record current count",
            "task count",
            "current count",
            "contains 20",
            "record runner name",
            "record env name",
            "named llm_coding_agent_v0",
            "current real llm runner",
            "conda env skilladmit",
            "current v4",
            "current skilladmit",
            "current local",
            "this machine",
            "local proxy",
            "local environment",
            "current project configuration",
            "current project setup",
            "current provider configuration",
            "frozen controller",
            "frozen file path",
            "artifact location",
            "prediction file",
            "prediction output",
            "python executable",
            "current generated",
            "generated task count",
            "current openai-compatible endpoint",
            "current evaluation command",
            "current handoff",
            "document path",
            "repository documentation state",
            "only applies to this repository",
            "only applies to this local machine",
            "only applies to this experiment phase",
            "only valid if this user's",
            "stale if benchmark expands",
            "record executable path",
            "record frozen file path",
            "store prediction output path",
            "record command for continuation",
            "record document path",
            "openai_base_url",
            "configured base url",
            "env var name",
            "value location",
            "project .env",
            "project's setup",
        ]
        tag_score = 1.0 if "context_specific" in tags else 0.0
        return max(tag_score, self._marker_score(text, markers))

    def _runner_noise_signal(self, sample: dict[str, Any], text: str) -> float:
        tags = set(sample.get("tags", []))
        markers = [
            "runner-level noise",
            "infrastructure noise",
            "empty model response",
            "transient model",
            "retry logic",
            "not a task-solving strategy",
            "not enter the agent",
        ]
        tag_score = 1.0 if "runner_artifact" in tags else 0.0
        return max(tag_score, self._marker_score(text, markers))

    def _noise_likelihood(self, text: str) -> float:
        markers = ["temporary", "transient", "random", "network", "flaky"]
        return self._marker_score(text, markers)

    def _marker_score(self, text: str, markers: list[str]) -> float:
        hits = sum(1 for marker in markers if marker in text)
        return min(1.0, hits / max(1, min(len(markers), 5)))
