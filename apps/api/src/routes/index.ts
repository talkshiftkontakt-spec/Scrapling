import type { FastifyInstance } from "fastify";

import {
  analysisResultSchema,
  componentAssetSchema,
  discoveredWebsiteSchema,
  pageScreenshotBatchSchema,
  processingStatusSchema,
  screenshotArtifactSchema
} from "@design-intelligence/shared";
import {
  getReferenceById,
  getWebsiteById,
  getWebsiteStats,
  getScreenshotForWebsite,
  recordPageCaptureFailure,
  listNeedsPageCapture,
  listBrowsableReferences,
  listPageScreenshotsForWebsite,
  listPendingCapture,
  listReferences,
  recordPageCaptureFailure,
  storeAnalysisRun,
  storePageScreenshots,
  storeQualityScore,
  storeScreenshotArtifact,
  updateWebsiteStatus,
  upsertDiscoveredWebsites
} from "@design-intelligence/database";
import {
  ComponentExtractionService,
  DesignCriticService,
  DesignSpecificationService,
  ReferencePackService,
  RetrievalService,
  WebsiteProcessingService
} from "@design-intelligence/design-intelligence";

export function registerRoutes<TApp extends FastifyInstance>(app: TApp): void {
  const componentExtractionService = new ComponentExtractionService();
  const specificationService = new DesignSpecificationService();
  const criticService = new DesignCriticService();
  const referencePackService = new ReferencePackService();
  const retrievalService = new RetrievalService();
  const processor = new WebsiteProcessingService();

  app.get("/health", async () => ({ status: "ok" }));

  app.get("/stats", async () => getWebsiteStats());

  app.post("/ingestion/discovered-websites", async (request) => {
    const payload = discoveredWebsiteSchema.array().parse(request.body);
    const records = await upsertDiscoveredWebsites(payload);
    return {
      accepted: records.length,
      records
    };
  });

  app.get("/ingestion/pending-capture", async (request) => {
    const limit = Number((request.query as { limit?: string }).limit ?? "20");
    return listPendingCapture(Number.isFinite(limit) ? limit : 20);
  });

  app.get("/ingestion/needs-page-capture", async (request) => {
    const limit = Number((request.query as { limit?: string }).limit ?? "20");
    return listNeedsPageCapture(Number.isFinite(limit) ? limit : 20);
  });

  app.post("/ingestion/mark-status/:websiteId", async (request) => {
    const { websiteId } = request.params as { websiteId: string };
    const body = request.body as { status?: string };
    const status = processingStatusSchema.parse(body.status);
    await updateWebsiteStatus(websiteId, status);
    return { ok: true, websiteId, status };
  });

  app.post("/ingestion/page-capture-failure/:websiteId", async (request) => {
    const { websiteId } = request.params as { websiteId: string };
    const body = request.body as { error?: string };
    await recordPageCaptureFailure(websiteId, body.error ?? "unknown");
    return { ok: true, websiteId };
  });

  app.post("/ingestion/screenshots", async (request) => {
    const payload = screenshotArtifactSchema.parse(request.body);
    const screenshot = await storeScreenshotArtifact(payload);
    return {
      accepted: true,
      screenshot
    };
  });

  app.post("/ingestion/page-screenshots", async (request) => {
    const payload = pageScreenshotBatchSchema.parse(request.body);
    const result = await storePageScreenshots(payload.websiteId, payload.pages, payload.primaryScreenshot);
    return {
      accepted: true,
      ...result
    };
  });

  app.post("/ingestion/process/:websiteId", async (request) => {
    const { websiteId } = request.params as { websiteId: string };
    const storedScreenshot = await getScreenshotForWebsite(websiteId);
    if (!storedScreenshot) {
      return { processed: false, reason: "screenshot_not_found" };
    }

    const website = await getWebsiteById(websiteId);
    if (!website) {
      return { processed: false, reason: "website_not_found" };
    }

    const screenshot = screenshotArtifactSchema.parse({
      websiteId,
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
      websiteId,
      screenshot,
      websiteName: website.websiteName,
      source: website.source,
      categories: website.categories,
      tags: website.tags
    });

    await storeAnalysisRun(analysis);
    const score = processor.score(analysis);
    await storeQualityScore(score);

    return {
      processed: true,
      websiteId,
      accepted: score.accepted,
      finalScore: score.finalScore,
      rejectionReasons: score.rejectionReasons
    };
  });

  app.get("/references", async (request) => {
    const query = request.query as { status?: "accepted" | "rejected" | "captured"; limit?: string; browse?: string };
    const limit = Number(query.limit ?? "50");

    if (query.browse === "1" || query.browse === "true") {
      return listBrowsableReferences({
        limit: Number.isFinite(limit) ? Math.min(limit, 200) : 50
      });
    }

    const options: Parameters<typeof listReferences>[0] = {
      limit: Number.isFinite(limit) ? Math.min(limit, 200) : 50
    };
    if (query.status) {
      options.status = query.status;
    }
    return listReferences(options);
  });

  app.get("/references/:websiteId", async (request, reply) => {
    const { websiteId } = request.params as { websiteId: string };
    const reference = await getReferenceById(websiteId);
    if (!reference) {
      return reply.status(404).send({ error: "reference_not_found" });
    }
    return reference;
  });

  app.get("/references/:websiteId/pages", async (request, reply) => {
    const { websiteId } = request.params as { websiteId: string };
    const website = await getWebsiteById(websiteId);
    if (!website) {
      return reply.status(404).send({ error: "reference_not_found" });
    }
    return listPageScreenshotsForWebsite(websiteId);
  });

  app.get("/search/references", async (request) => {
    const query = (request.query as { q?: string }).q ?? "premium ai saas";
    return retrievalService.buildReferenceResponse({
      websites: [`reference-for-${query}`],
      components: [`component-for-${query}`],
      styles: ["editorial", "linear-like"]
    });
  });

  app.post("/components/extract-preview", async (request) => {
    const body = request.body as { analysis: unknown; screenshot: unknown };
    const analysis = analysisResultSchema.parse(body.analysis);
    const screenshot = screenshotArtifactSchema.parse(body.screenshot);
    const components = componentExtractionService.extract(analysis, screenshot);

    return componentAssetSchema.array().parse(components);
  });

  app.post("/reference-packs/suggest", async (request) => {
    const body = request.body as { theme: string; websiteIds: string[]; componentIds: string[]; styleLabels: string[] };
    return referencePackService.createSuggestedPack(body.theme, body.websiteIds, body.componentIds, body.styleLabels);
  });

  app.post("/design-specifications/generate", async (request) => {
    const body = request.body as { productIdea: string; references: string[] };
    return specificationService.generate(body.productIdea, body.references);
  });

  app.post("/design-critic/evaluate", async (request) => {
    const body = request.body as { referenceSummary: string; generatedSummary: string };
    return criticService.critique(body);
  });
}
