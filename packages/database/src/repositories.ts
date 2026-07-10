import { and, desc, eq, inArray, isNull, or, sql } from "drizzle-orm";

import type {
  AnalysisResult,
  DiscoveredWebsite,
  ProcessingStatus,
  ProviderName,
  QualityScore,
  ScreenshotArtifact
} from "@design-intelligence/shared";

import { getDb } from "./client.js";
import {
  analysisRuns,
  categories,
  providers,
  qualityScores,
  screenshots,
  tags,
  websiteCategories,
  websites,
  websiteSources,
  websiteTags
} from "./schema.js";

const PROVIDER_LABELS: Record<ProviderName, string> = {
  awwwards: "Awwwards",
  landbook: "Land-book",
  godly: "Godly",
  lapa_ninja: "Lapa Ninja",
  one_page_love: "One Page Love"
};

export interface PendingCaptureWebsite {
  websiteId: string;
  websiteName: string;
  canonicalUrl: string;
  normalizedUrl: string;
  source: ProviderName;
  categories: string[];
  tags: string[];
}

export interface PendingProcessingWebsite extends PendingCaptureWebsite {
  screenshotId: string;
  screenshotDriveUrl: string;
}

export interface ReferenceSummary {
  websiteId: string;
  websiteName: string;
  canonicalUrl: string;
  processingStatus: ProcessingStatus;
  finalScore: number | null;
  thumbnailDriveUrl: string | null;
  style: string | null;
  industry: string | null;
}

function normalizeUrl(url: string): string {
  const parsed = new URL(url);
  parsed.hash = "";
  parsed.searchParams.sort();
  const normalized = parsed.toString();
  return normalized.endsWith("/") ? normalized.slice(0, -1) : normalized;
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

async function ensureProvider(providerName: ProviderName): Promise<string> {
  const db = getDb();
  await db
    .insert(providers)
    .values({ slug: providerName, name: PROVIDER_LABELS[providerName] })
    .onConflictDoNothing();

  const [provider] = await db.select({ id: providers.id }).from(providers).where(eq(providers.slug, providerName)).limit(1);
  if (!provider) {
    throw new Error(`Provider ${providerName} could not be ensured.`);
  }

  return provider.id;
}

async function ensureCategory(category: string): Promise<string> {
  const db = getDb();
  const slug = slugify(category);
  await db.insert(categories).values({ slug, label: category }).onConflictDoNothing();
  const [row] = await db.select({ id: categories.id }).from(categories).where(eq(categories.slug, slug)).limit(1);
  if (!row) {
    throw new Error(`Category ${category} could not be ensured.`);
  }
  return row.id;
}

async function ensureTag(tag: string): Promise<string> {
  const db = getDb();
  const slug = slugify(tag);
  await db.insert(tags).values({ slug, label: tag }).onConflictDoNothing();
  const [row] = await db.select({ id: tags.id }).from(tags).where(eq(tags.slug, slug)).limit(1);
  if (!row) {
    throw new Error(`Tag ${tag} could not be ensured.`);
  }
  return row.id;
}

async function getWebsiteTags(websiteId: string): Promise<string[]> {
  const db = getDb();
  const rows = await db
    .select({ label: tags.label })
    .from(websiteTags)
    .innerJoin(tags, eq(websiteTags.tagId, tags.id))
    .where(eq(websiteTags.websiteId, websiteId));
  return rows.map((row) => row.label);
}

async function getWebsiteCategories(websiteId: string): Promise<string[]> {
  const db = getDb();
  const rows = await db
    .select({ label: categories.label })
    .from(websiteCategories)
    .innerJoin(categories, eq(websiteCategories.categoryId, categories.id))
    .where(eq(websiteCategories.websiteId, websiteId));
  return rows.map((row) => row.label);
}

async function getWebsiteSource(websiteId: string): Promise<ProviderName> {
  const db = getDb();
  const [row] = await db
    .select({ slug: providers.slug })
    .from(websiteSources)
    .innerJoin(providers, eq(websiteSources.providerId, providers.id))
    .where(eq(websiteSources.websiteId, websiteId))
    .limit(1);

  if (!row) {
    return "awwwards";
  }

  return row.slug as ProviderName;
}

export async function updateWebsiteStatus(websiteId: string, status: ProcessingStatus) {
  const db = getDb();
  await db
    .update(websites)
    .set({
      processingStatus: status,
      updatedAt: new Date(),
      ...(status === "accepted" ? { acceptedAt: new Date() } : {})
    })
    .where(eq(websites.id, websiteId));
}

export async function upsertDiscoveredWebsites(records: DiscoveredWebsite[]) {
  const db = getDb();
  const acceptedRecords: Array<{
    websiteId: string;
    websiteName: string;
    canonicalUrl: string;
    normalizedUrl: string;
    source: ProviderName;
  }> = [];

  for (const record of records) {
    const normalizedUrl = normalizeUrl(record.url);
    const providerId = await ensureProvider(record.source);
    const [existing] = await db.select({ id: websites.id }).from(websites).where(eq(websites.normalizedUrl, normalizedUrl)).limit(1);

    const websiteId = existing
      ? existing.id
      : (
          await db
            .insert(websites)
            .values({
              websiteName: record.websiteName,
              canonicalUrl: record.url,
              normalizedUrl,
              discoveredAt: new Date(record.discoveredAt),
              metadata: record.metadata
            })
            .returning({ id: websites.id })
        )[0]!.id;

    await db
      .insert(websiteSources)
      .values({
        websiteId,
        providerId,
        providerReference: record.providerReference,
        discoveredAt: new Date(record.discoveredAt),
        metadata: record.metadata
      })
      .onConflictDoNothing();

    for (const category of record.categories) {
      const categoryId = await ensureCategory(category);
      await db.insert(websiteCategories).values({ websiteId, categoryId }).onConflictDoNothing();
    }

    for (const tag of record.tags) {
      const tagId = await ensureTag(tag);
      await db.insert(websiteTags).values({ websiteId, tagId }).onConflictDoNothing();
    }

    acceptedRecords.push({
      websiteId,
      websiteName: record.websiteName,
      canonicalUrl: record.url,
      normalizedUrl,
      source: record.source
    });
  }

  return acceptedRecords;
}

export async function claimPendingCapture(limit = 20): Promise<PendingCaptureWebsite[]> {
  const db = getDb();

  await db.execute(sql`
    UPDATE websites
    SET processing_status = 'failed', updated_at = NOW()
    WHERE processing_status = 'capture_pending'
      AND updated_at < NOW() - INTERVAL '3 minutes'
  `);

  const claimed = await db.transaction(async (tx) => {
    const picked = await tx.execute<{ id: string; website_name: string; canonical_url: string; normalized_url: string }>(sql`
      WITH picked AS (
        SELECT w.id
        FROM websites w
        LEFT JOIN screenshots s ON s.website_id = w.id
        WHERE s.id IS NULL
          AND w.processing_status IN ('discovered', 'failed')
        ORDER BY w.discovered_at ASC
        LIMIT ${limit}
        FOR UPDATE OF w SKIP LOCKED
      )
      UPDATE websites w
      SET processing_status = 'capture_pending', updated_at = NOW()
      FROM picked
      WHERE w.id = picked.id
      RETURNING w.id, w.website_name, w.canonical_url, w.normalized_url
    `);

    return picked.rows;
  });

  const results: PendingCaptureWebsite[] = [];
  for (const row of claimed) {
    results.push({
      websiteId: row.id,
      websiteName: row.website_name,
      canonicalUrl: row.canonical_url,
      normalizedUrl: row.normalized_url,
      source: await getWebsiteSource(row.id),
      categories: await getWebsiteCategories(row.id),
      tags: await getWebsiteTags(row.id)
    });
  }

  return results;
}

export async function listPendingCapture(limit = 20): Promise<PendingCaptureWebsite[]> {
  return claimPendingCapture(limit);
}

export async function listPendingProcessing(limit = 20): Promise<PendingProcessingWebsite[]> {
  const db = getDb();
  const rows = await db
    .select({
      websiteId: websites.id,
      websiteName: websites.websiteName,
      canonicalUrl: websites.canonicalUrl,
      normalizedUrl: websites.normalizedUrl,
      screenshotId: screenshots.id,
      screenshotDriveUrl: screenshots.screenshotDriveUrl
    })
    .from(websites)
    .innerJoin(screenshots, eq(screenshots.websiteId, websites.id))
    .leftJoin(qualityScores, eq(qualityScores.websiteId, websites.id))
    .where(
      and(
        isNull(qualityScores.id),
        inArray(websites.processingStatus, ["captured", "analysis_pending", "analyzed", "scoring_pending"])
      )
    )
    .limit(limit);

  const results: PendingProcessingWebsite[] = [];
  for (const row of rows) {
    results.push({
      websiteId: row.websiteId,
      websiteName: row.websiteName,
      canonicalUrl: row.canonicalUrl,
      normalizedUrl: row.normalizedUrl,
      screenshotId: row.screenshotId,
      screenshotDriveUrl: row.screenshotDriveUrl,
      source: await getWebsiteSource(row.websiteId),
      categories: await getWebsiteCategories(row.websiteId),
      tags: await getWebsiteTags(row.websiteId)
    });
  }

  return results;
}

export async function getWebsiteById(websiteId: string): Promise<PendingCaptureWebsite | null> {
  const db = getDb();
  const [row] = await db
    .select({
      websiteId: websites.id,
      websiteName: websites.websiteName,
      canonicalUrl: websites.canonicalUrl,
      normalizedUrl: websites.normalizedUrl
    })
    .from(websites)
    .where(eq(websites.id, websiteId))
    .limit(1);

  if (!row) {
    return null;
  }

  return {
    websiteId: row.websiteId,
    websiteName: row.websiteName,
    canonicalUrl: row.canonicalUrl,
    normalizedUrl: row.normalizedUrl,
    source: await getWebsiteSource(row.websiteId),
    categories: await getWebsiteCategories(row.websiteId),
    tags: await getWebsiteTags(row.websiteId)
  };
}

export async function getScreenshotForWebsite(websiteId: string) {
  const db = getDb();
  const [row] = await db.select().from(screenshots).where(eq(screenshots.websiteId, websiteId)).limit(1);
  return row ?? null;
}

export async function storeScreenshotArtifact(artifact: ScreenshotArtifact) {
  const db = getDb();

  await db
    .insert(screenshots)
    .values({
      websiteId: artifact.websiteId,
      screenshotDriveFileId: artifact.screenshotDriveFileId,
      screenshotDriveUrl: artifact.screenshotDriveUrl,
      thumbnailDriveFileId: artifact.thumbnailDriveFileId,
      thumbnailDriveUrl: artifact.thumbnailDriveUrl,
      width: artifact.width,
      height: artifact.height,
      checksumSha256: artifact.checksumSha256,
      capturedAt: new Date(artifact.capturedAt),
      metadata: artifact.metadata
    })
    .onConflictDoUpdate({
      target: screenshots.websiteId,
      set: {
        screenshotDriveFileId: artifact.screenshotDriveFileId,
        screenshotDriveUrl: artifact.screenshotDriveUrl,
        thumbnailDriveFileId: artifact.thumbnailDriveFileId,
        thumbnailDriveUrl: artifact.thumbnailDriveUrl,
        width: artifact.width,
        height: artifact.height,
        checksumSha256: artifact.checksumSha256,
        capturedAt: new Date(artifact.capturedAt),
        metadata: artifact.metadata
      }
    });

  await updateWebsiteStatus(artifact.websiteId, "captured");

  const [stored] = await db.select().from(screenshots).where(eq(screenshots.websiteId, artifact.websiteId)).limit(1);
  return stored;
}

export async function storeAnalysisRun(analysis: AnalysisResult) {
  const db = getDb();

  const [stored] = await db
    .insert(analysisRuns)
    .values({
      websiteId: analysis.websiteId,
      modelProvider: analysis.modelProvider,
      model: analysis.model,
      style: analysis.style,
      industry: analysis.industry,
      typography: analysis.typography,
      colourPalette: analysis.colourPalette,
      layout: analysis.layout,
      visualDensity: analysis.visualDensity,
      navigationStyle: analysis.navigationStyle,
      designKeywords: analysis.designKeywords,
      summary: analysis.summary,
      mobileFirstLikelihood: String(analysis.mobileFirstLikelihood),
      animationLikelihood: String(analysis.animationLikelihood),
      designMaturity: analysis.designMaturity,
      rawResponse: analysis.rawResponse,
      normalizedPayload: analysis
    })
    .returning();

  await updateWebsiteStatus(analysis.websiteId, "analyzed");
  return stored;
}

export async function storeQualityScore(score: QualityScore) {
  const db = getDb();

  const [stored] = await db
    .insert(qualityScores)
    .values({
      websiteId: score.websiteId,
      originality: String(score.originality),
      typographyQuality: String(score.typographyQuality),
      layoutQuality: String(score.layoutQuality),
      visualHierarchy: String(score.visualHierarchy),
      consistency: String(score.consistency),
      premiumFeel: String(score.premiumFeel),
      uxMaturity: String(score.uxMaturity),
      finalScore: String(score.finalScore),
      accepted: score.accepted,
      rejectionReasons: score.rejectionReasons
    })
    .onConflictDoUpdate({
      target: qualityScores.websiteId,
      set: {
        originality: String(score.originality),
        typographyQuality: String(score.typographyQuality),
        layoutQuality: String(score.layoutQuality),
        visualHierarchy: String(score.visualHierarchy),
        consistency: String(score.consistency),
        premiumFeel: String(score.premiumFeel),
        uxMaturity: String(score.uxMaturity),
        finalScore: String(score.finalScore),
        accepted: score.accepted,
        rejectionReasons: score.rejectionReasons
      }
    })
    .returning();

  await updateWebsiteStatus(score.websiteId, score.accepted ? "accepted" : "rejected");
  return stored;
}

export async function listReferences(options: { status?: ProcessingStatus; limit?: number } = {}) {
  const db = getDb();
  const limit = options.limit ?? 50;

  const conditions = options.status
    ? eq(websites.processingStatus, options.status)
    : or(eq(websites.processingStatus, "accepted"), eq(websites.processingStatus, "rejected"));

  const rows = await db
    .select({
      websiteId: websites.id,
      websiteName: websites.websiteName,
      canonicalUrl: websites.canonicalUrl,
      processingStatus: websites.processingStatus,
      finalScore: qualityScores.finalScore,
      thumbnailDriveUrl: screenshots.thumbnailDriveUrl,
      style: analysisRuns.style,
      industry: analysisRuns.industry
    })
    .from(websites)
    .leftJoin(qualityScores, eq(qualityScores.websiteId, websites.id))
    .leftJoin(screenshots, eq(screenshots.websiteId, websites.id))
    .leftJoin(analysisRuns, eq(analysisRuns.websiteId, websites.id))
    .where(conditions)
    .orderBy(desc(sql`COALESCE(${qualityScores.finalScore}, 0)`))
    .limit(limit);

  return rows.map((row) => ({
    websiteId: row.websiteId,
    websiteName: row.websiteName,
    canonicalUrl: row.canonicalUrl,
    processingStatus: row.processingStatus as ProcessingStatus,
    finalScore: row.finalScore ? Number(row.finalScore) : null,
    thumbnailDriveUrl: row.thumbnailDriveUrl,
    style: row.style,
    industry: row.industry
  })) satisfies ReferenceSummary[];
}

export async function getWebsiteStats() {
  const db = getDb();
  const rows = await db
    .select({
      status: websites.processingStatus,
      count: sql<number>`count(*)::int`
    })
    .from(websites)
    .groupBy(websites.processingStatus);

  return Object.fromEntries(rows.map((row) => [row.status, row.count]));
}
