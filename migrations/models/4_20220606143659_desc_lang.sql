-- upgrade --
ALTER TABLE "lang" ADD "description" VARCHAR(255);
-- downgrade --
ALTER TABLE "lang" DROP COLUMN "description";
