import type { AnalysisResult, QualityScore } from "@design-intelligence/shared";

export interface DuplicateCandidate {
  leftWebsiteId: string;
  rightWebsiteId: string;
  method: "normalized_url" | "metadata" | "visual_embedding" | "template_family";
  similarityScore: number;
}

export class DeduplicationService {
  public compareByNormalizedUrl(leftUrl: string, rightUrl: string): DuplicateCandidate | null {
    if (leftUrl === rightUrl) {
      return {
        leftWebsiteId: leftUrl,
        rightWebsiteId: rightUrl,
        method: "normalized_url",
        similarityScore: 1
      };
    }

    return null;
  }

  public compareByAnalysis(left: AnalysisResult, right: AnalysisResult): DuplicateCandidate | null {
    const overlap = left.designKeywords.filter((keyword: string) => right.designKeywords.includes(keyword)).length;
    const score = overlap / Math.max(left.designKeywords.length, right.designKeywords.length, 1);

    if (score < 0.6) {
      return null;
    }

    return {
      leftWebsiteId: left.websiteId,
      rightWebsiteId: right.websiteId,
      method: "metadata",
      similarityScore: Number(score.toFixed(3))
    };
  }

  public chooseCanonical(left: QualityScore, right: QualityScore): string {
    return left.finalScore >= right.finalScore ? left.websiteId : right.websiteId;
  }
}
