import { z } from "zod";

export const processingStatusSchema = z.enum([
  "discovered",
  "capture_pending",
  "captured",
  "analysis_pending",
  "analyzed",
  "scoring_pending",
  "accepted",
  "rejected",
  "duplicate",
  "archived",
  "failed"
]);

export const componentKindSchema = z.enum([
  "hero",
  "navigation",
  "pricing",
  "feature",
  "testimonial",
  "dashboard",
  "sidebar",
  "form",
  "cta",
  "footer"
]);

export const providerNameSchema = z.enum([
  "awwwards",
  "landbook",
  "godly",
  "lapa_ninja",
  "one_page_love"
]);

export const discoveredWebsiteSchema = z.object({
  websiteName: z.string().min(1),
  url: z.string().url(),
  source: providerNameSchema,
  categories: z.array(z.string().min(1)).default([]),
  tags: z.array(z.string().min(1)).default([]),
  providerReference: z.string().min(1),
  discoveredAt: z.string().datetime(),
  metadata: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).default({})
});

export const screenshotArtifactSchema = z.object({
  websiteId: z.string().uuid(),
  screenshotDriveFileId: z.string().min(1),
  screenshotDriveUrl: z.string().url(),
  thumbnailDriveFileId: z.string().min(1),
  thumbnailDriveUrl: z.string().url(),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  checksumSha256: z.string().min(32),
  capturedAt: z.string().datetime(),
  localTempPath: z.string().optional(),
  metadata: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).default({})
});

export const analysisResultSchema = z.object({
  websiteId: z.string().uuid(),
  modelProvider: z.enum(["openai", "gemini", "heuristic"]),
  model: z.string().min(1),
  style: z.string().min(1),
  industry: z.string().min(1),
  typography: z.array(z.string().min(1)),
  colourPalette: z.array(z.string().min(1)),
  layout: z.string().min(1),
  visualDensity: z.string().min(1),
  navigationStyle: z.string().min(1),
  designKeywords: z.array(z.string().min(1)),
  summary: z.string().min(1),
  mobileFirstLikelihood: z.number().min(0).max(1),
  animationLikelihood: z.number().min(0).max(1),
  designMaturity: z.string().min(1),
  rawResponse: z.string().min(1)
});

export const qualityScoreSchema = z.object({
  websiteId: z.string().uuid(),
  originality: z.number().min(1).max(10),
  typographyQuality: z.number().min(1).max(10),
  layoutQuality: z.number().min(1).max(10),
  visualHierarchy: z.number().min(1).max(10),
  consistency: z.number().min(1).max(10),
  premiumFeel: z.number().min(1).max(10),
  uxMaturity: z.number().min(1).max(10),
  finalScore: z.number().min(1).max(10),
  rejectionReasons: z.array(z.string()),
  accepted: z.boolean()
});

export const componentAssetSchema = z.object({
  websiteId: z.string().uuid(),
  componentKind: componentKindSchema,
  name: z.string().min(1),
  driveFileId: z.string().min(1),
  driveUrl: z.string().url(),
  thumbnailDriveUrl: z.string().url().optional(),
  bbox: z.object({
    x: z.number().min(0),
    y: z.number().min(0),
    width: z.number().positive(),
    height: z.number().positive()
  }),
  summary: z.string().min(1),
  designKeywords: z.array(z.string().min(1)),
  embeddingInput: z.string().min(1),
  confidence: z.number().min(0).max(1)
});

export const referencePackSchema = z.object({
  packName: z.string().min(1),
  theme: z.string().min(1),
  qualityFloor: z.number().min(1).max(10),
  curationNotes: z.string().optional(),
  websiteIds: z.array(z.string().uuid()),
  componentIds: z.array(z.string().uuid()),
  styleLabels: z.array(z.string().min(1))
});

export const ingestionFailureSchema = z.object({
  stage: z.string().min(1),
  retryable: z.boolean(),
  message: z.string().min(1),
  details: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).default({})
});

export type ProcessingStatus = z.infer<typeof processingStatusSchema>;
export type ComponentKind = z.infer<typeof componentKindSchema>;
export type ProviderName = z.infer<typeof providerNameSchema>;
export type DiscoveredWebsite = z.infer<typeof discoveredWebsiteSchema>;
export type ScreenshotArtifact = z.infer<typeof screenshotArtifactSchema>;
export type AnalysisResult = z.infer<typeof analysisResultSchema>;
export type QualityScore = z.infer<typeof qualityScoreSchema>;
export type ComponentAsset = z.infer<typeof componentAssetSchema>;
export type ReferencePack = z.infer<typeof referencePackSchema>;
export type IngestionFailure = z.infer<typeof ingestionFailureSchema>;
