CREATE TYPE "public"."component_kind" AS ENUM('hero', 'navigation', 'pricing', 'feature', 'testimonial', 'dashboard', 'sidebar', 'form', 'cta', 'footer');--> statement-breakpoint
CREATE TYPE "public"."processing_status" AS ENUM('discovered', 'capture_pending', 'captured', 'analysis_pending', 'analyzed', 'scoring_pending', 'accepted', 'rejected', 'duplicate', 'archived', 'failed');--> statement-breakpoint
CREATE TYPE "public"."provider_name" AS ENUM('awwwards', 'landbook', 'godly', 'lapa_ninja', 'one_page_love');--> statement-breakpoint
CREATE TYPE "public"."similarity_method" AS ENUM('normalized_url', 'metadata', 'visual_embedding', 'template_family');--> statement-breakpoint
CREATE TABLE "analysis_runs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid NOT NULL,
	"model_provider" varchar(64) NOT NULL,
	"model" varchar(128) NOT NULL,
	"prompt_version" varchar(64) DEFAULT 'v1' NOT NULL,
	"style" text NOT NULL,
	"industry" text NOT NULL,
	"typography" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"colour_palette" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"layout" text NOT NULL,
	"visual_density" text NOT NULL,
	"navigation_style" text NOT NULL,
	"design_keywords" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"summary" text NOT NULL,
	"mobile_first_likelihood" numeric(3, 2) NOT NULL,
	"animation_likelihood" numeric(3, 2) NOT NULL,
	"design_maturity" text NOT NULL,
	"raw_response" text NOT NULL,
	"normalized_payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "audit_events" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"entity_type" varchar(64) NOT NULL,
	"entity_id" uuid NOT NULL,
	"event_type" varchar(128) NOT NULL,
	"payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "categories" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" varchar(128) NOT NULL,
	"label" varchar(128) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "categories_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "component_assets" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"component_id" uuid NOT NULL,
	"screenshot_id" uuid NOT NULL,
	"drive_file_id" text NOT NULL,
	"drive_url" text NOT NULL,
	"thumbnail_drive_url" text,
	"bbox_x" integer NOT NULL,
	"bbox_y" integer NOT NULL,
	"bbox_width" integer NOT NULL,
	"bbox_height" integer NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "components" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid NOT NULL,
	"component_kind" "component_kind" NOT NULL,
	"name" varchar(256) NOT NULL,
	"summary" text NOT NULL,
	"design_keywords" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"embedding_input" text NOT NULL,
	"confidence" numeric(3, 2) NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "processing_jobs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid,
	"stage" varchar(64) NOT NULL,
	"status" varchar(64) DEFAULT 'pending' NOT NULL,
	"attempts" integer DEFAULT 0 NOT NULL,
	"max_attempts" integer DEFAULT 5 NOT NULL,
	"payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"last_error" text,
	"scheduled_at" timestamp with time zone DEFAULT now() NOT NULL,
	"started_at" timestamp with time zone,
	"completed_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "providers" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" "provider_name" NOT NULL,
	"name" varchar(128) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "providers_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "quality_scores" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid NOT NULL,
	"originality" numeric(4, 2) NOT NULL,
	"typography_quality" numeric(4, 2) NOT NULL,
	"layout_quality" numeric(4, 2) NOT NULL,
	"visual_hierarchy" numeric(4, 2) NOT NULL,
	"consistency" numeric(4, 2) NOT NULL,
	"premium_feel" numeric(4, 2) NOT NULL,
	"ux_maturity" numeric(4, 2) NOT NULL,
	"final_score" numeric(4, 2) NOT NULL,
	"accepted" boolean NOT NULL,
	"rejection_reasons" jsonb DEFAULT '[]'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "quality_scores_final_score_range" CHECK ("quality_scores"."final_score" >= 0 AND "quality_scores"."final_score" <= 10)
);
--> statement-breakpoint
CREATE TABLE "reference_pack_items" (
	"reference_pack_id" uuid NOT NULL,
	"website_id" uuid,
	"component_id" uuid,
	"rank" integer DEFAULT 0 NOT NULL,
	"rationale" text,
	CONSTRAINT "reference_pack_items_reference_pack_id_rank_pk" PRIMARY KEY("reference_pack_id","rank")
);
--> statement-breakpoint
CREATE TABLE "reference_packs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"pack_name" varchar(256) NOT NULL,
	"theme" varchar(256) NOT NULL,
	"quality_floor" numeric(4, 2) NOT NULL,
	"curation_notes" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "reference_packs_pack_name_unique" UNIQUE("pack_name")
);
--> statement-breakpoint
CREATE TABLE "screenshots" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid NOT NULL,
	"screenshot_drive_file_id" text NOT NULL,
	"screenshot_drive_url" text NOT NULL,
	"thumbnail_drive_file_id" text NOT NULL,
	"thumbnail_drive_url" text NOT NULL,
	"width" integer NOT NULL,
	"height" integer NOT NULL,
	"checksum_sha256" varchar(128) NOT NULL,
	"captured_at" timestamp with time zone NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "similarity_edges" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"left_website_id" uuid NOT NULL,
	"right_website_id" uuid NOT NULL,
	"method" "similarity_method" NOT NULL,
	"similarity_score" numeric(4, 3) NOT NULL,
	"decision" varchar(64) DEFAULT 'candidate' NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "styles" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" varchar(128) NOT NULL,
	"label" varchar(128) NOT NULL,
	"description" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "styles_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "tags" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" varchar(128) NOT NULL,
	"label" varchar(128) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "tags_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE "website_categories" (
	"website_id" uuid NOT NULL,
	"category_id" uuid NOT NULL,
	CONSTRAINT "website_categories_website_id_category_id_pk" PRIMARY KEY("website_id","category_id")
);
--> statement-breakpoint
CREATE TABLE "website_sources" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid NOT NULL,
	"provider_id" uuid NOT NULL,
	"provider_reference" text NOT NULL,
	"discovered_at" timestamp with time zone NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL
);
--> statement-breakpoint
CREATE TABLE "website_styles" (
	"website_id" uuid NOT NULL,
	"style_id" uuid NOT NULL,
	"confidence" numeric(3, 2) NOT NULL,
	CONSTRAINT "website_styles_website_id_style_id_pk" PRIMARY KEY("website_id","style_id")
);
--> statement-breakpoint
CREATE TABLE "website_tags" (
	"website_id" uuid NOT NULL,
	"tag_id" uuid NOT NULL,
	CONSTRAINT "website_tags_website_id_tag_id_pk" PRIMARY KEY("website_id","tag_id")
);
--> statement-breakpoint
CREATE TABLE "websites" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_name" varchar(256) NOT NULL,
	"canonical_url" text NOT NULL,
	"normalized_url" text NOT NULL,
	"source_status" varchar(64) DEFAULT 'active' NOT NULL,
	"processing_status" "processing_status" DEFAULT 'discovered' NOT NULL,
	"discovered_at" timestamp with time zone NOT NULL,
	"accepted_at" timestamp with time zone,
	"is_canonical" boolean DEFAULT true NOT NULL,
	"canonical_website_id" uuid,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "analysis_runs" ADD CONSTRAINT "analysis_runs_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "component_assets" ADD CONSTRAINT "component_assets_component_id_components_id_fk" FOREIGN KEY ("component_id") REFERENCES "public"."components"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "component_assets" ADD CONSTRAINT "component_assets_screenshot_id_screenshots_id_fk" FOREIGN KEY ("screenshot_id") REFERENCES "public"."screenshots"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "components" ADD CONSTRAINT "components_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "processing_jobs" ADD CONSTRAINT "processing_jobs_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "quality_scores" ADD CONSTRAINT "quality_scores_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "reference_pack_items" ADD CONSTRAINT "reference_pack_items_reference_pack_id_reference_packs_id_fk" FOREIGN KEY ("reference_pack_id") REFERENCES "public"."reference_packs"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "reference_pack_items" ADD CONSTRAINT "reference_pack_items_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "reference_pack_items" ADD CONSTRAINT "reference_pack_items_component_id_components_id_fk" FOREIGN KEY ("component_id") REFERENCES "public"."components"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "screenshots" ADD CONSTRAINT "screenshots_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "similarity_edges" ADD CONSTRAINT "similarity_edges_left_website_id_websites_id_fk" FOREIGN KEY ("left_website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "similarity_edges" ADD CONSTRAINT "similarity_edges_right_website_id_websites_id_fk" FOREIGN KEY ("right_website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_categories" ADD CONSTRAINT "website_categories_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_categories" ADD CONSTRAINT "website_categories_category_id_categories_id_fk" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_sources" ADD CONSTRAINT "website_sources_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_sources" ADD CONSTRAINT "website_sources_provider_id_providers_id_fk" FOREIGN KEY ("provider_id") REFERENCES "public"."providers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_styles" ADD CONSTRAINT "website_styles_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_styles" ADD CONSTRAINT "website_styles_style_id_styles_id_fk" FOREIGN KEY ("style_id") REFERENCES "public"."styles"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_tags" ADD CONSTRAINT "website_tags_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "website_tags" ADD CONSTRAINT "website_tags_tag_id_tags_id_fk" FOREIGN KEY ("tag_id") REFERENCES "public"."tags"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "analysis_runs_website_idx" ON "analysis_runs" USING btree ("website_id");--> statement-breakpoint
CREATE INDEX "audit_events_entity_idx" ON "audit_events" USING btree ("entity_type","entity_id");--> statement-breakpoint
CREATE INDEX "component_assets_component_idx" ON "component_assets" USING btree ("component_id");--> statement-breakpoint
CREATE INDEX "components_website_idx" ON "components" USING btree ("website_id");--> statement-breakpoint
CREATE INDEX "components_kind_idx" ON "components" USING btree ("component_kind");--> statement-breakpoint
CREATE INDEX "processing_jobs_stage_idx" ON "processing_jobs" USING btree ("stage","status");--> statement-breakpoint
CREATE INDEX "processing_jobs_website_idx" ON "processing_jobs" USING btree ("website_id");--> statement-breakpoint
CREATE UNIQUE INDEX "quality_scores_website_idx" ON "quality_scores" USING btree ("website_id");--> statement-breakpoint
CREATE INDEX "quality_scores_final_score_idx" ON "quality_scores" USING btree ("final_score");--> statement-breakpoint
CREATE UNIQUE INDEX "screenshots_website_idx" ON "screenshots" USING btree ("website_id");--> statement-breakpoint
CREATE INDEX "similarity_edges_left_idx" ON "similarity_edges" USING btree ("left_website_id");--> statement-breakpoint
CREATE INDEX "similarity_edges_right_idx" ON "similarity_edges" USING btree ("right_website_id");--> statement-breakpoint
CREATE UNIQUE INDEX "website_sources_unique_idx" ON "website_sources" USING btree ("provider_id","provider_reference");--> statement-breakpoint
CREATE INDEX "website_sources_website_idx" ON "website_sources" USING btree ("website_id");--> statement-breakpoint
CREATE UNIQUE INDEX "websites_normalized_url_idx" ON "websites" USING btree ("normalized_url");--> statement-breakpoint
CREATE INDEX "websites_processing_status_idx" ON "websites" USING btree ("processing_status");--> statement-breakpoint
CREATE INDEX "websites_canonical_idx" ON "websites" USING btree ("canonical_website_id");