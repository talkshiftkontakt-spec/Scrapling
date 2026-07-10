import type { ReferencePack } from "@design-intelligence/shared";

export interface SearchReferenceResult {
  websites: string[];
  components: string[];
  styles: string[];
}

export class ReferencePackService {
  public createSuggestedPack(theme: string, websiteIds: string[], componentIds: string[], styleLabels: string[]): ReferencePack {
    return {
      packName: `${theme} Premium Pack`,
      theme,
      qualityFloor: 7.5,
      websiteIds,
      componentIds,
      styleLabels,
      curationNotes: `System-assisted pack for ${theme}.`
    };
  }
}

export class RetrievalService {
  public buildReferenceResponse(input: SearchReferenceResult) {
    return {
      references: input.websites,
      components: input.components,
      styles: input.styles
    };
  }
}
