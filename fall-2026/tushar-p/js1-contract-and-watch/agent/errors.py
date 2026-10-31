"""Errors that stop a run. The CLI prints the message and exits with status 2."""


class AgentError(Exception):
    """Base class: the run stops and the message is shown."""


class ConfigError(AgentError):
    """Bad config.json, or ANTHROPIC_API_KEY missing without --no-claude."""


class PersonaError(AgentError):
    """A required résumé field is absent, has the wrong type, or is an empty list."""


class RuleUndefinedError(AgentError):
    """The persona holds a value the contract's rule is not written for."""


class HostNotAllowed(AgentError):
    """A URL is not https or its host is not on the allow-list."""


class FetchError(AgentError):
    """The board could not be fetched, or answered with a non-200 status."""


class RawInputError(AgentError):
    """A board response cannot be used as run input."""


class StateError(AgentError):
    """The state file exists but is not a JSON list of integer ids."""


class ValidationError(AgentError):
    """A justification or a Claude reply does not match the contract's format."""


class ClaudeAuthError(AgentError):
    """The Claude API rejected the API key (HTTP 401). The run stops at the first call."""
