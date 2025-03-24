CREATE TABLE IF NOT EXISTS "lots" (
	"id"	INTEGER,
	"volume"	INTEGER,
	"dtime"	TEXT,
	"cnt"	INTEGER,
	"region"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "rockets" (
	"id"	INTEGER,
	"volume"	INTEGER,
	"dtime"	TEXT,
	"cnt"	INTEGER,
	"region"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "sold" (
	"id"	INTEGER,
	"volume"	INTEGER,
	"dtime"	TEXT,
	"cnt"	INTEGER,
	"region"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "coefficients" (
	"id"	INTEGER,
	"volume"	INTEGER,
	"dtime"	TEXT,
	"ten_min"	REAL,
	"one_hour"	REAL,
	"one_day"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE IF NOT EXISTS "volumes" (
    "id"    INTEGER,
	"volume" INTEGER UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
