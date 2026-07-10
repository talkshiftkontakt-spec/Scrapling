import type { FastifyInstance } from "fastify";

import { componentAssetSchema, discoveredWebsiteSchema, screenshotArtifactSchema } from "@design-intelligence/shared";
import {
  ComponentExtractionService,
  DesignCriticService,
  DesignSpecificationService,
  ReferencePackService,
  RetrievalService
} from "@design-intelligence/design-intelligence";

export function registerRoutes(app: FastifyInstance): void {
  const componentExtractionService = new ComponentExtractionService();
  const specificationService = new DesignSpecificationService();
  const criticService = new DesignCriticService();
  const referencePackService = new ReferencePackService();
  const retrievalService = new RetrievalService();

  app.get("/health", async () => ({ status: "ok" }));

  app.post("/ingestion/discovered-websites", async (request) => {
    const payload = discoveredWebsiteSchema.array().parse(request.body);
    return {
      accepted: payload.length,
      records: payload.map((record) => ({ normalizedUrl: new URL(record.url).toString(), source: record.source }))
    };
  });

  app.post("/ingestion/screenshots", async (request) => {
    const payload = screenshotArtifactSchema.parse(request.body);
    return {
      accepted: true,
      screenshot: payload
    };
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
    const analysis = body.analysis as Parameters<ComponentExtractionService["extract"]>[0];
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
