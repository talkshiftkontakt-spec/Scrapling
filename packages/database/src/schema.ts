import {
  boolean,
  check,
  index,
  integer,
  jsonb,
  numeric,
  pgEnum,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar
} from "drizzle-orm/pg-core";
import { sql } from "drizzle-orm";

export const processingStatusEnum = pgEnum("processing_status", [
  "discovered",
  "capture_pending",
  "captured",
  "analysis_pending",
  "analyzed",
  "scoring_pending",
  "accepted",
  "rejected",
  "duplicate",
  "archived",
  "failed"
]);

export const providerEnum = pgEnum("provider_name", [
  "awwwards",
  "landbook",
  "godly",
  "lapa_ninja",
  "one_page_love"
]);

export const componentKindEnum = pgEnum("component_kind", [
  "hero",
  "navigation",
  "pricing",
  "feature",
  "testimonial",
  "dashboard",
  "sidebar",
  "form",
  "cta",
  "footer"
]);

export const similarityMethodEnum = pgEnum("similarity_method", [
  "normalized_url",
  "metadata",
  "visual_embedding",
  "template_family"
]);

export const providers = pgTable("providers", {
  id: uuid("id").defaultRandom().primaryKey(),
  slug: providerEnum("slug").notNull().unique(),
  name: varchar("name", { length: 128 }).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
});

export const websites = pgTable("websites", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteName: varchar("website_name", { length: 256 }).notNull(),
  canonicalUrl: text("canonical_url").notNull(),
  normalizedUrl: text("normalized_url").notNull(),
  sourceStatus: varchar("source_status", { length: 64 }).default("active").notNull(),
  processingStatus: processingStatusEnum("processing_status").default("discovered").notNull(),
  discoveredAt: timestamp("discovered_at", { withTimezone: true }).notNull(),
  acceptedAt: timestamp("accepted_at", { withTimezone: true }),
  isCanonical: boolean("is_canonical").default(true).notNull(),
  canonicalWebsiteId: uuid("canonical_website_id"),
  metadata: jsonb("metadata").default(sql`'{}'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  normalizedUrlIdx: uniqueIndex("websites_normalized_url_idx").on(table.normalizedUrl),
  processingStatusIdx: index("websites_processing_status_idx").on(table.processingStatus),
  canonicalIdx: index("websites_canonical_idx").on(table.canonicalWebsiteId)
}));

export const websiteSources = pgTable("website_sources", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  providerId: uuid("provider_id").references(() => providers.id, { onDelete: "cascade" }).notNull(),
  providerReference: text("provider_reference").notNull(),
  discoveredAt: timestamp("discovered_at", { withTimezone: true }).notNull(),
  metadata: jsonb("metadata").default(sql`'{}'::jsonb`).notNull()
}, (table) => ({
  uniqueProviderSource: uniqueIndex("website_sources_unique_idx").on(table.providerId, table.providerReference),
  websiteSourcesWebsiteIdx: index("website_sources_website_idx").on(table.websiteId)
}));

export const categories = pgTable("categories", {
  id: uuid("id").defaultRandom().primaryKey(),
  slug: varchar("slug", { length: 128 }).notNull().unique(),
  label: varchar("label", { length: 128 }).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
});

export const tags = pgTable("tags", {
  id: uuid("id").defaultRandom().primaryKey(),
  slug: varchar("slug", { length: 128 }).notNull().unique(),
  label: varchar("label", { length: 128 }).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
});

export const websiteCategories = pgTable("website_categories", {
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  categoryId: uuid("category_id").references(() => categories.id, { onDelete: "cascade" }).notNull()
}, (table) => ({
  pk: primaryKey({ columns: [table.websiteId, table.categoryId] })
}));

export const websiteTags = pgTable("website_tags", {
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  tagId: uuid("tag_id").references(() => tags.id, { onDelete: "cascade" }).notNull()
}, (table) => ({
  pk: primaryKey({ columns: [table.websiteId, table.tagId] })
}));

export const screenshots = pgTable("screenshots", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  screenshotDriveFileId: text("screenshot_drive_file_id").notNull(),
  screenshotDriveUrl: text("screenshot_drive_url").notNull(),
  thumbnailDriveFileId: text("thumbnail_drive_file_id").notNull(),
  thumbnailDriveUrl: text("thumbnail_drive_url").notNull(),
  width: integer("width").notNull(),
  height: integer("height").notNull(),
  checksumSha256: varchar("checksum_sha256", { length: 128 }).notNull(),
  capturedAt: timestamp("captured_at", { withTimezone: true }).notNull(),
  metadata: jsonb("metadata").default(sql`'{}'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  websiteScreenshotIdx: uniqueIndex("screenshots_website_idx").on(table.websiteId)
}));

export const analysisRuns = pgTable("analysis_runs", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  modelProvider: varchar("model_provider", { length: 64 }).notNull(),
  model: varchar("model", { length: 128 }).notNull(),
  promptVersion: varchar("prompt_version", { length: 64 }).default("v1").notNull(),
  style: text("style").notNull(),
  industry: text("industry").notNull(),
  typography: jsonb("typography").default(sql`'[]'::jsonb`).notNull(),
  colourPalette: jsonb("colour_palette").default(sql`'[]'::jsonb`).notNull(),
  layout: text("layout").notNull(),
  visualDensity: text("visual_density").notNull(),
  navigationStyle: text("navigation_style").notNull(),
  designKeywords: jsonb("design_keywords").default(sql`'[]'::jsonb`).notNull(),
  summary: text("summary").notNull(),
  mobileFirstLikelihood: numeric("mobile_first_likelihood", { precision: 3, scale: 2 }).notNull(),
  animationLikelihood: numeric("animation_likelihood", { precision: 3, scale: 2 }).notNull(),
  designMaturity: text("design_maturity").notNull(),
  rawResponse: text("raw_response").notNull(),
  normalizedPayload: jsonb("normalized_payload").default(sql`'{}'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  analysisWebsiteIdx: index("analysis_runs_website_idx").on(table.websiteId)
}));

export const qualityScores = pgTable("quality_scores", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  originality: numeric("originality", { precision: 4, scale: 2 }).notNull(),
  typographyQuality: numeric("typography_quality", { precision: 4, scale: 2 }).notNull(),
  layoutQuality: numeric("layout_quality", { precision: 4, scale: 2 }).notNull(),
  visualHierarchy: numeric("visual_hierarchy", { precision: 4, scale: 2 }).notNull(),
  consistency: numeric("consistency", { precision: 4, scale: 2 }).notNull(),
  premiumFeel: numeric("premium_feel", { precision: 4, scale: 2 }).notNull(),
  uxMaturity: numeric("ux_maturity", { precision: 4, scale: 2 }).notNull(),
  finalScore: numeric("final_score", { precision: 4, scale: 2 }).notNull(),
  accepted: boolean("accepted").notNull(),
  rejectionReasons: jsonb("rejection_reasons").default(sql`'[]'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  qualityWebsiteIdx: uniqueIndex("quality_scores_website_idx").on(table.websiteId),
  qualityFinalScoreIdx: index("quality_scores_final_score_idx").on(table.finalScore),
  qualityScoreCheck: check("quality_scores_final_score_range", sql`${table.finalScore} >= 0 AND ${table.finalScore} <= 10`)
}));

export const components = pgTable("components", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  componentKind: componentKindEnum("component_kind").notNull(),
  name: varchar("name", { length: 256 }).notNull(),
  summary: text("summary").notNull(),
  designKeywords: jsonb("design_keywords").default(sql`'[]'::jsonb`).notNull(),
  embeddingInput: text("embedding_input").notNull(),
  confidence: numeric("confidence", { precision: 3, scale: 2 }).notNull(),
  metadata: jsonb("metadata").default(sql`'{}'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  componentsWebsiteIdx: index("components_website_idx").on(table.websiteId),
  componentsKindIdx: index("components_kind_idx").on(table.componentKind)
}));

export const componentAssets = pgTable("component_assets", {
  id: uuid("id").defaultRandom().primaryKey(),
  componentId: uuid("component_id").references(() => components.id, { onDelete: "cascade" }).notNull(),
  screenshotId: uuid("screenshot_id").references(() => screenshots.id, { onDelete: "cascade" }).notNull(),
  driveFileId: text("drive_file_id").notNull(),
  driveUrl: text("drive_url").notNull(),
  thumbnailDriveUrl: text("thumbnail_drive_url"),
  bboxX: integer("bbox_x").notNull(),
  bboxY: integer("bbox_y").notNull(),
  bboxWidth: integer("bbox_width").notNull(),
  bboxHeight: integer("bbox_height").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  componentAssetsComponentIdx: index("component_assets_component_idx").on(table.componentId)
}));

export const styles = pgTable("styles", {
  id: uuid("id").defaultRandom().primaryKey(),
  slug: varchar("slug", { length: 128 }).notNull().unique(),
  label: varchar("label", { length: 128 }).notNull(),
  description: text("description"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
});

export const websiteStyles = pgTable("website_styles", {
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  styleId: uuid("style_id").references(() => styles.id, { onDelete: "cascade" }).notNull(),
  confidence: numeric("confidence", { precision: 3, scale: 2 }).notNull()
}, (table) => ({
  pk: primaryKey({ columns: [table.websiteId, table.styleId] })
}));

export const similarityEdges = pgTable("similarity_edges", {
  id: uuid("id").defaultRandom().primaryKey(),
  leftWebsiteId: uuid("left_website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  rightWebsiteId: uuid("right_website_id").references(() => websites.id, { onDelete: "cascade" }).notNull(),
  method: similarityMethodEnum("method").notNull(),
  similarityScore: numeric("similarity_score", { precision: 4, scale: 3 }).notNull(),
  decision: varchar("decision", { length: 64 }).default("candidate").notNull(),
  metadata: jsonb("metadata").default(sql`'{}'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  similarityLeftIdx: index("similarity_edges_left_idx").on(table.leftWebsiteId),
  similarityRightIdx: index("similarity_edges_right_idx").on(table.rightWebsiteId)
}));

export const referencePacks = pgTable("reference_packs", {
  id: uuid("id").defaultRandom().primaryKey(),
  packName: varchar("pack_name", { length: 256 }).notNull().unique(),
  theme: varchar("theme", { length: 256 }).notNull(),
  qualityFloor: numeric("quality_floor", { precision: 4, scale: 2 }).notNull(),
  curationNotes: text("curation_notes"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull()
});

export const referencePackItems = pgTable("reference_pack_items", {
  referencePackId: uuid("reference_pack_id").references(() => referencePacks.id, { onDelete: "cascade" }).notNull(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }),
  componentId: uuid("component_id").references(() => components.id, { onDelete: "cascade" }),
  rank: integer("rank").default(0).notNull(),
  rationale: text("rationale")
}, (table) => ({
  pk: primaryKey({ columns: [table.referencePackId, table.rank] })
}));

export const processingJobs = pgTable("processing_jobs", {
  id: uuid("id").defaultRandom().primaryKey(),
  websiteId: uuid("website_id").references(() => websites.id, { onDelete: "cascade" }),
  stage: varchar("stage", { length: 64 }).notNull(),
  status: varchar("status", { length: 64 }).default("pending").notNull(),
  attempts: integer("attempts").default(0).notNull(),
  maxAttempts: integer("max_attempts").default(5).notNull(),
  payload: jsonb("payload").default(sql`'{}'::jsonb`).notNull(),
  lastError: text("last_error"),
  scheduledAt: timestamp("scheduled_at", { withTimezone: true }).defaultNow().notNull(),
  startedAt: timestamp("started_at", { withTimezone: true }),
  completedAt: timestamp("completed_at", { withTimezone: true }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  processingJobsStageIdx: index("processing_jobs_stage_idx").on(table.stage, table.status),
  processingJobsWebsiteIdx: index("processing_jobs_website_idx").on(table.websiteId)
}));

export const auditEvents = pgTable("audit_events", {
  id: uuid("id").defaultRandom().primaryKey(),
  entityType: varchar("entity_type", { length: 64 }).notNull(),
  entityId: uuid("entity_id").notNull(),
  eventType: varchar("event_type", { length: 128 }).notNull(),
  payload: jsonb("payload").default(sql`'{}'::jsonb`).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull()
}, (table) => ({
  auditEventsEntityIdx: index("audit_events_entity_idx").on(table.entityType, table.entityId)
}));
