import { eq } from "drizzle-orm";

import type { DiscoveredWebsite, ProviderName, ScreenshotArtifact } from "@design-intelligence/shared";

import { getDb } from "./client.js";
import {
  categories,
  providers,
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

export async function upsertDiscoveredWebsites(records: DiscoveredWebsite[]) {
  const db = getDb();
  const acceptedRecords: Array<{ websiteId: string; normalizedUrl: string; source: ProviderName }> = [];

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

    acceptedRecords.push({ websiteId, normalizedUrl, source: record.source });
  }

  return acceptedRecords;
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

  const [stored] = await db.select().from(screenshots).where(eq(screenshots.websiteId, artifact.websiteId)).limit(1);
  return stored;
}
