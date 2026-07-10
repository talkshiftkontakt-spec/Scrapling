import { QdrantClient } from "@qdrant/js-client-rest";

import { readEnv, type ComponentAsset, type ReferencePack } from "@design-intelligence/shared";

export type SearchTarget = "websites" | "components" | "styles";

export interface SearchDocument {
  id: string;
  vector: number[];
  payload: Record<string, unknown>;
}

export interface SearchQuery {
  collection: SearchTarget;
  vector: number[];
  limit?: number;
  minScore?: number;
  filter?: Record<string, unknown>;
}

const env = readEnv();

export class DesignSearchIndex {
  private readonly client = new QdrantClient(
    env.QDRANT_API_KEY
      ? {
          url: env.QDRANT_URL,
          apiKey: env.QDRANT_API_KEY
        }
      : {
          url: env.QDRANT_URL
        }
  );

  public async upsertDocuments(collection: SearchTarget, documents: SearchDocument[]): Promise<void> {
    if (documents.length === 0) {
      return;
    }

    await this.client.upsert(collection, {
      wait: true,
      points: documents.map((document) => ({
        id: document.id,
        vector: document.vector,
        payload: document.payload
      }))
    });
  }

  public async search(query: SearchQuery) {
    const searchRequest: Parameters<QdrantClient["search"]>[1] = {
      vector: query.vector,
      limit: query.limit ?? 8,
      filter: query.filter as never
    };

    if (query.minScore !== undefined) {
      searchRequest.score_threshold = query.minScore;
    }

    const results = await this.client.search(query.collection, searchRequest);

    return results;
  }

  public buildComponentPayload(component: ComponentAsset) {
    return {
      websiteId: component.websiteId,
      componentKind: component.componentKind,
      name: component.name,
      keywords: component.designKeywords,
      confidence: component.confidence
    };
  }

  public buildReferencePackPayload(pack: ReferencePack) {
    return {
      packName: pack.packName,
      theme: pack.theme,
      qualityFloor: pack.qualityFloor,
      websiteIds: pack.websiteIds,
      componentIds: pack.componentIds,
      styleLabels: pack.styleLabels
    };
  }
}
