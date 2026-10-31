"""Refusals from CONTRACT.md §3. Each one is a refusal, not a crash."""


class Refusal(Exception):
    """Base class for every refusal the contract promises."""

    exit_code = 2


class DisallowedHost(Refusal):
    """R1: the agent was asked to fetch a host that is not on the allow-list."""


class NonPersonaResume(Refusal):
    """R2: the resume given is not a validated fictional persona."""


class FetchFailed(Refusal):
    """R1: non-200, a redirect, or a response that is not JSON."""


class ValidatorRejected(Refusal):
    """R3: a model's output did not meet the prompt contract's output format."""
