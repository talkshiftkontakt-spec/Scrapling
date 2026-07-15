import { readAiEnv } from "@design-intelligence/shared";

import { HeuristicAnalysisService } from "./heuristic-analysis.js";
import { VisualAnalysisService, type AnalysisInput } from "./analysis.js";
import { QualityScoringService } from "./scoring.js";
import type { AnalysisResult } from "@design-intelligence/shared";

export class WebsiteProcessingService {
  private readonly heuristic = new HeuristicAnalysisService();
  private readonly scoring = new QualityScoringService();
  private readonly visual: VisualAnalysisService | null;

  public constructor() {
    const env = readAiEnv();
    this.visual = env.OPENAI_API_KEY || env.GEMINI_API_KEY ? new VisualAnalysisService() : null;
  }

  public async analyzeWebsite(input: AnalysisInput & {
    websiteName: string;
    source: import("@design-intelligence/shared").ProviderName;
    categories: string[];
    tags: string[];
  }): Promise<AnalysisResult> {
    if (this.visual && process.env.OPENAI_API_KEY) {
      return this.visual.analyze("openai", input);
    }

    if (this.visual && process.env.GEMINI_API_KEY) {
      return this.visual.analyze("gemini", input);
    }

    return this.heuristic.analyze({
      websiteId: input.websiteId,
      websiteName: input.websiteName,
      source: input.source,
      categories: input.categories,
      tags: input.tags,
      screenshotUrl: input.screenshot.screenshotDriveUrl
    });
  }

  public score(analysis: AnalysisResult) {
    return this.scoring.score(analysis);
  }
}
