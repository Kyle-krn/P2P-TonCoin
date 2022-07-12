-- upgrade --
ALTER TABLE "currency_key" ADD "is_active" BOOL NOT NULL  DEFAULT False;
-- downgrade --
ALTER TABLE "currency_key" DROP COLUMN "is_active";
