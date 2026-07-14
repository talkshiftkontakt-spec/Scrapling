import { analysisResultSchema, type DiscoveredWebsite, type ProviderName } from "@design-intelligence/shared";
import type { AnalysisResult } from "@design-intelligence/shared";

const CURATED_SOURCES: ProviderName[] = ["awwwards", "godly", "landbook", "lapa_ninja", "one_page_love"];

const STYLE_BY_SOURCE: Record<ProviderName, string> = {
  awwwards: "award-winning editorial",
  landbook: "clean product landing",
  godly: "premium web craft",
  lapa_ninja: "marketing landing",
  one_page_love: "one-page storytelling"
};

export interface HeuristicAnalysisInput {
  websiteId: string;
  websiteName: string;
  source: ProviderName;
  categories: string[];
  tags: string[];
  screenshotUrl?: string;
}

export class HeuristicAnalysisService {
  public analyze(input: HeuristicAnalysisInput): AnalysisResult {
    const isCurated = CURATED_SOURCES.includes(input.source);
    const style = input.categories[0] ?? STYLE_BY_SOURCE[input.source];
    const industry = this.inferIndustry(input.categories, input.tags);
    const typography = this.inferTypography(style);
    const colourPalette = ["neutral base", "single accent", "high contrast text"];
    const layout = style.toLowerCase().includes("editorial") ? "asymmetric editorial grid" : "structured responsive grid";
    const designKeywords = [
      ...input.tags.slice(0, 4),
      isCurated ? "curated-source" : "discovered-source",
      isCurated ? "premium" : "reference"
    ].filter(Boolean);

    const payload = {
      websiteId: input.websiteId,
      modelProvider: "heuristic" as const,
      model: "curated-source-v1",
      style,
      industry,
      typography,
      colourPalette,
      layout,
      visualDensity: "balanced",
      navigationStyle: "minimal top navigation",
      designKeywords,
      summary: `${input.websiteName} presents a ${style} layout with clear hierarchy and curated ${input.source} provenance.`,
      mobileFirstLikelihood: 0.78,
      animationLikelihood: 0.42,
      designMaturity: isCurated ? "mature" : "developing",
      rawResponse: JSON.stringify({ source: input.source, screenshotUrl: input.screenshotUrl })
    };

    return analysisResultSchema.parse(payload);
  }

  public fromDiscoveredWebsite(websiteId: string, record: DiscoveredWebsite): AnalysisResult {
    return this.analyze({
      websiteId,
      websiteName: record.websiteName,
      source: record.source,
      categories: record.categories,
      tags: record.tags
    });
  }

  private inferIndustry(categories: string[], tags: string[]): string {
    const haystack = [...categories, ...tags].join(" ").toLowerCase();
    if (haystack.includes("fintech") || haystack.includes("finance")) return "fintech";
    if (haystack.includes("ai") || haystack.includes("saas")) return "ai saas";
    if (haystack.includes("health") || haystack.includes("wellness")) return "wellness";
    if (haystack.includes("agency") || haystack.includes("studio")) return "creative agency";
    return "digital product";
  }

  private inferTypography(style: string): string[] {
    if (style.toLowerCase().includes("editorial")) {
      return ["display serif headline", "neutral sans body", "tight letter-spacing"];
    }
    return ["geometric sans headline", "neutral sans body", "comfortable line-height"];
  }
}
