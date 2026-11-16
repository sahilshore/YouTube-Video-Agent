"""Typed exceptions used to present actionable errors to the UI."""


class YouTubeAgentError(Exception):
    """Base application error."""


class ConfigurationError(YouTubeAgentError):
    """A required setting is missing or invalid."""


class ProviderError(YouTubeAgentError):
    """An LLM or media provider failed."""


class ValidationError(YouTubeAgentError):
    """Generated or user-provided data failed validation."""


class MediaError(YouTubeAgentError):
    """Media could not be found, downloaded, or validated."""


class RenderError(YouTubeAgentError):
    """FFmpeg could not render or validate an output."""

