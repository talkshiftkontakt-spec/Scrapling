import { qualityScoreSchema, type AnalysisResult, type QualityScore } from "@design-intelligence/shared";

const REJECTION_SCORE_THRESHOLD = 7;

export class QualityScoringService {
  public score(analysis: AnalysisResult): QualityScore {
    const densityPenalty = analysis.visualDensity.toLowerCase().includes("clutter") ? 1.5 : 0;
    const premiumFeel = analysis.designKeywords.some((keyword: string) => keyword.toLowerCase().includes("premium")) ? 8.8 : 7.1;
    const typographyQuality = analysis.typography.length >= 2 ? 8.2 : 7.1;
    const layoutQuality = analysis.layout.toLowerCase().includes("grid") ? 8.4 : 7.5;
    const visualHierarchy = analysis.summary.toLowerCase().includes("clear hierarchy") ? 8.5 : 7.2;
    const consistency = analysis.designMaturity.toLowerCase().includes("mature") ? 8.3 : 7.3;
    const originality = analysis.designKeywords.some((keyword: string) => keyword.toLowerCase().includes("generic")) ? 5.8 : 8.0;
    const uxMaturity = Math.max(6.5, analysis.mobileFirstLikelihood * 3 + analysis.animationLikelihood * 2 + 5.5);

    const finalScore = Number((((premiumFeel + typographyQuality + layoutQuality + visualHierarchy + consistency + originality + uxMaturity) / 7) - densityPenalty).toFixed(2));
    const rejectionReasons: string[] = [];

    if (originality < 7) {
      rejectionReasons.push("generic_template_signals");
    }
    if (finalScore < REJECTION_SCORE_THRESHOLD) {
      rejectionReasons.push("below_quality_threshold");
    }

    return qualityScoreSchema.parse({
      websiteId: analysis.websiteId,
      originality,
      typographyQuality,
      layoutQuality,
      visualHierarchy,
      consistency,
      premiumFeel,
      uxMaturity,
      finalScore,
      rejectionReasons,
      accepted: finalScore >= REJECTION_SCORE_THRESHOLD && rejectionReasons.length === 0
    });
  }
}
