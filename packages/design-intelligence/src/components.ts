import {
  componentAssetSchema,
  type AnalysisResult,
  type ComponentAsset,
  type ComponentKind,
  type ScreenshotArtifact
} from "@design-intelligence/shared";

const DEFAULT_COMPONENTS: Array<{ kind: ComponentKind; name: string }> = [
  { kind: "hero", name: "Primary Hero" },
  { kind: "navigation", name: "Primary Navigation" },
  { kind: "pricing", name: "Pricing Section" },
  { kind: "dashboard", name: "Dashboard Preview" },
  { kind: "cta", name: "Primary CTA" }
];

export class ComponentExtractionService {
  public extract(analysis: AnalysisResult, screenshot: ScreenshotArtifact): ComponentAsset[] {
    const halfWidth = Math.floor(screenshot.width / 2);
    const segmentHeight = Math.max(240, Math.floor(screenshot.height / 5));

    return DEFAULT_COMPONENTS.map((definition, index) => componentAssetSchema.parse({
      websiteId: analysis.websiteId,
      componentKind: definition.kind,
      name: definition.name,
      driveFileId: `${analysis.websiteId}-${definition.kind}`,
      driveUrl: screenshot.screenshotDriveUrl,
      thumbnailDriveUrl: screenshot.thumbnailDriveUrl,
      bbox: {
        x: 0,
        y: index * segmentHeight,
        width: halfWidth,
        height: segmentHeight
      },
      summary: `${definition.name} extracted from ${analysis.style} ${analysis.industry} design reference.`,
      designKeywords: analysis.designKeywords,
      embeddingInput: `${definition.kind} ${analysis.summary}`,
      confidence: 0.72
    }));
  }
}
