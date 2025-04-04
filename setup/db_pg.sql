CREATE TABLE IF NOT EXISTS "public"."lots" (
    "id" serial NOT NULL,
    PRIMARY KEY ("id"),
    "volume" integer NOT NULL,
    "dtime" timestamp NOT NULL,
    "cnt" integer NOT NULL,
    "region" text NOT NULL
);

CREATE TABLE IF NOT EXISTS "public"."rockets" (
    "id" serial NOT NULL,
    PRIMARY KEY ("id"),
    "volume" integer NOT NULL,
    "dtime" timestamp NOT NULL,
    "cnt" integer NOT NULL,
    "region" text NOT NULL
);

CREATE TABLE IF NOT EXISTS "public"."anomaly" (
    "id" serial NOT NULL,
    PRIMARY KEY ("id"),
    "volume" integer NOT NULL,
    "dtime" timestamp NOT NULL,
    "cnt" integer NOT NULL,
    "region" text NOT NULL
);

CREATE TABLE IF NOT EXISTS "public"."sold" (
    "id" serial NOT NULL,
    PRIMARY KEY ("id"),
    "volume" integer NOT NULL,
    "dtime" timestamp NOT NULL,
    "cnt" integer NOT NULL,
    "region" text NOT NULL
);

-- CREATE TABLE IF NOT EXISTS "public"."coefficients" (
--     "id" serial NOT NULL,
--     PRIMARY KEY ("id"),
--     "volume" integer NOT NULL,
--     "dtime" timestamp NOT NULL,
-- 	"ten_min" REAL NOT NULL,
-- 	"one_hour" REAL NOT NULL,
-- 	"one_day" REAL NOT NULL
-- );


CREATE TABLE IF NOT EXISTS "public"."volumes" (
    "id" serial NOT NULL,
    PRIMARY KEY ("id"),
    "volume" integer NOT NULL UNIQUE
);
