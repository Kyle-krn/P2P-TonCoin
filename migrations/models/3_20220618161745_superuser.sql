-- upgrade --
ALTER TABLE "staff" ADD "superuser" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "staff" DROP COLUMN "superuser";
