-- upgrade --
ALTER TABLE "lang" ADD "button" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "lang" DROP COLUMN "button";
