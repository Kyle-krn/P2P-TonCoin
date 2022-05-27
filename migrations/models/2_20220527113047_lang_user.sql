-- upgrade --
ALTER TABLE "user" ADD "lang" VARCHAR(30);
-- downgrade --
ALTER TABLE "user" DROP COLUMN "lang";
