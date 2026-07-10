from __future__ import annotations

import os
from dataclasses import dataclass, field


def _parse_origins(raw: str | None) -> list[str]:
    if not raw:
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass
class ApiSettings:
    api_key: str | None = field(default_factory=lambda: os.getenv("SPORTSDATA_API_KEY"))
    cors_origins: list[str] = field(
        default_factory=lambda: _parse_origins(os.getenv("SPORTSDATA_CORS_ORIGINS"))
    )
    default_page_size: int = int(os.getenv("SPORTSDATA_DEFAULT_PAGE_SIZE", "50"))
    max_page_size: int = int(os.getenv("SPORTSDATA_MAX_PAGE_SIZE", "500"))
    require_api_key: bool = os.getenv("SPORTSDATA_REQUIRE_API_KEY", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    def page_size(self, requested: int | None) -> int:
        if requested is None:
            return self.default_page_size
        return max(1, min(requested, self.max_page_size))
