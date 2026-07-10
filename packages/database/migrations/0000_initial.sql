CREATE TYPE processing_status AS ENUM ('discovered', 'capture_pending', 'captured', 'analysis_pending', 'analyzed', 'scoring_pending', 'accepted', 'rejected', 'duplicate', 'archived', 'failed');
CREATE TYPE provider_name AS ENUM ('awwwards', 'landbook', 'godly', 'lapa_ninja', 'one_page_love');
CREATE TYPE component_kind AS ENUM ('hero', 'navigation', 'pricing', 'feature', 'testimonial', 'dashboard', 'sidebar', 'form', 'cta', 'footer');
CREATE TYPE similarity_method AS ENUM ('normalized_url', 'metadata', 'visual_embedding', 'template_family');
