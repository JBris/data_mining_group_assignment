DROP TABLE IF EXISTS "public"."data";
CREATE TABLE "public"."data" (
    "channel_id" integer,
    "channel_key" integer,
    "date_time" timestamp,
    "usage" numeric,
    "site" integer,
    "channel_pair" integer
) WITH (oids = false);