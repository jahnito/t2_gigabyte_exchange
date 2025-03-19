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

CREATE TABLE  IF NOT EXISTS "sold" (
	"id"	INTEGER,
	"volume"	INTEGER,
	"dtime"	TEXT,
	"cnt"	INTEGER,
	"region"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

