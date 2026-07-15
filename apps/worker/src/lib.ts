import {
  getWebsiteStats,
  getScreenshotForWebsite,
  listPendingProcessing,
  storeAnalysisRun,
  storeQualityScore
} from "@design-intelligence/database";
import { WebsiteProcessingService } from "@design-intelligence/design-intelligence";
import { screenshotArtifactSchema } from "@design-intelligence/shared";

export async function processPendingWebsites(limit = 20) {
  const processor = new WebsiteProcessingService();
  const pending = await listPendingProcessing(limit);
  const results = [];

  for (const website of pending) {
    const storedScreenshot = await getScreenshotForWebsite(website.websiteId);
    if (!storedScreenshot) {
      continue;
    }

    const screenshot = screenshotArtifactSchema.parse({
      websiteId: website.websiteId,
      screenshotDriveFileId: storedScreenshot.screenshotDriveFileId,
      screenshotDriveUrl: storedScreenshot.screenshotDriveUrl,
      thumbnailDriveFileId: storedScreenshot.thumbnailDriveFileId,
      thumbnailDriveUrl: storedScreenshot.thumbnailDriveUrl,
      width: storedScreenshot.width,
      height: storedScreenshot.height,
      checksumSha256: storedScreenshot.checksumSha256,
      capturedAt: storedScreenshot.capturedAt.toISOString(),
      metadata: storedScreenshot.metadata as Record<string, string | number | boolean>
    });

    const analysis = await processor.analyzeWebsite({
      websiteId: website.websiteId,
      screenshot,
      websiteName: website.websiteName,
      source: website.source,
      categories: website.categories,
      tags: website.tags
    });

    const storedAnalysis = await storeAnalysisRun(analysis);
    const score = processor.score(analysis);
    const storedScore = await storeQualityScore(score);

    results.push({
      websiteId: website.websiteId,
      websiteName: website.websiteName,
      accepted: score.accepted,
      finalScore: score.finalScore,
      analysisId: storedAnalysis?.id,
      qualityScoreId: storedScore?.id
    });
  }

  return {
    processed: results.length,
    results,
    stats: await getWebsiteStats()
  };
}
