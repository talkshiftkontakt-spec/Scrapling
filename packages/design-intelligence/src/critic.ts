export interface DesignCriticInput {
  referenceSummary: string;
  generatedSummary: string;
}

export interface DesignCriticResult {
  genericity: number;
  spacingQuality: number;
  typographyQuality: number;
  hierarchyClarity: number;
  referenceAlignment: number;
  issues: string[];
  suggestions: string[];
}

export class DesignCriticService {
  public critique(input: DesignCriticInput): DesignCriticResult {
    const genericity = input.generatedSummary.toLowerCase().includes("generic") ? 4.8 : 8.1;
    const referenceAlignment = input.generatedSummary.includes(input.referenceSummary.slice(0, 12)) ? 8.4 : 6.7;

    return {
      genericity,
      spacingQuality: 7.8,
      typographyQuality: 7.9,
      hierarchyClarity: 8.0,
      referenceAlignment,
      issues: genericity < 7 ? ["Output still reads as template-derived."] : [],
      suggestions: [
        "Increase asymmetry and editorial pacing in the hero.",
        "Reduce repeated SaaS card patterns in mid-page sections.",
        "Strengthen typography contrast between section headers and support copy."
      ]
    };
  }
}
