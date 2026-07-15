"""Design intelligence ingestion built on top of Scrapling."""

from ingestion.scrapling.contracts import DiscoveredWebsiteRecord, ScreenshotArtifactRecord
from ingestion.scrapling.pipeline import DesignIngestionPipeline

__all__ = [
    "DesignIngestionPipeline",
    "DiscoveredWebsiteRecord",
    "ScreenshotArtifactRecord",
]
