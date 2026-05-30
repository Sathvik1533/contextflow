"""Exponential Backoff Utility — Production Resilience Layer.

THE PATTERN: Retry with Exponential Backoff + Jitter
  - Attempt 1 fails → wait 2s (+jitter) → retry
  - Attempt 2 fails → wait 4s (+jitter) → retry
  - Attempt 3 fails → wait 8s (+jitter) → raise

WHY THIS EXISTS:
  Groq free tier returns HTTP 429 (Too Many Requests) when overloaded.
  A flat sleep(10) retry is a guess. Exponential backoff is a proven
  production pattern used by AWS, Google, and every serious API client.

  Jitter (random extra delay) prevents "thundering herd" — the scenario
  where 1000 clients all retry at exactly the same moment and overload
  the server again immediately.

USAGE:
  from src.utils.retry import retry_with_backoff

  result = retry_with_backoff(
      fn=lambda: llm.invoke([message]),
      max_attempts=3,
      base_delay=2.0,
  )
"""

import logging
import random
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Error substrings that indicate a rate limit — catch only these, not all errors
RATE_LIMIT_SIGNALS = ("429", "rate limit", "rate_limit", "too many requests", "resource_exhausted")


def retry_with_backoff(
    fn: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 2.0,
    jitter: bool = True,
    label: str = "API call",
) -> T:
    """Execute fn with exponential backoff on rate limit errors.

    Args:
        fn: A zero-argument callable — the API call to retry.
            Use lambda if you need to pass arguments: lambda: llm.invoke([msg])
        max_attempts: Total number of attempts (default 3).
        base_delay: Starting delay in seconds (default 2.0).
            Delays: 2s → 4s → 8s for base_delay=2.0
        jitter: Add random 0–0.5s to each delay to prevent thundering herd.
        label: Human-readable name for log messages (e.g. "Observer API").

    Returns:
        Whatever fn() returns on success.

    Raises:
        The original exception if all attempts fail.
        Non-rate-limit exceptions are raised immediately (no retry).

    Data Flow:
        fn passed in → attempt 1 → success? return result
                                  → rate limit? wait (2^attempt * base_delay) → retry
                                  → other error? raise immediately (don't retry)
    """
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return fn()

        except Exception as exc:
            error_str = str(exc).lower()
            is_rate_limit = any(signal in error_str for signal in RATE_LIMIT_SIGNALS)

            if not is_rate_limit:
                # Not a rate limit — don't retry, raise immediately
                raise

            last_exception = exc
            is_last_attempt = attempt == max_attempts - 1

            if is_last_attempt:
                logger.error(
                    "%s failed after %d attempts. Last error: %s",
                    label, max_attempts, exc,
                )
                raise

            # Exponential delay: 2^attempt * base_delay
            # attempt=0 → 2s, attempt=1 → 4s, attempt=2 → 8s
            delay = (2 ** attempt) * base_delay
            if jitter:
                delay += random.uniform(0.0, 0.5)

            logger.warning(
                "%s rate limited (attempt %d/%d). Waiting %.1fs before retry.",
                label, attempt + 1, max_attempts, delay,
            )
            time.sleep(delay)

    # Should never reach here — last attempt raises above
    raise last_exception
