DO $$ BEGIN
 CREATE TYPE "public"."viewport_kind" AS ENUM('desktop', 'mobile');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 CREATE TYPE "public"."page_type" AS ENUM('home', 'pricing', 'about', 'features', 'contact', 'blog', 'login', 'dashboard', 'legal', 'careers', 'page');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "page_screenshots" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"website_id" uuid NOT NULL,
	"page_url" text NOT NULL,
	"page_path" text NOT NULL,
	"page_title" varchar(512),
	"page_type" "page_type" DEFAULT 'page' NOT NULL,
	"viewport" "viewport_kind" NOT NULL,
	"viewport_width" integer NOT NULL,
	"viewport_height" integer NOT NULL,
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
DO $$ BEGIN
 ALTER TABLE "page_screenshots" ADD CONSTRAINT "page_screenshots_website_id_websites_id_fk" FOREIGN KEY ("website_id") REFERENCES "public"."websites"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "page_screenshots_unique_idx" ON "page_screenshots" USING btree ("website_id","page_path","viewport");
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "page_screenshots_website_idx" ON "page_screenshots" USING btree ("website_id");
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "page_screenshots_type_idx" ON "page_screenshots" USING btree ("page_type");
