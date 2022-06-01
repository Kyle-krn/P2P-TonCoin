-- upgrade --
ALTER TABLE "order" ALTER COLUMN "final_price" DROP NOT NULL;
-- downgrade --
ALTER TABLE "order" ALTER COLUMN "final_price" SET NOT NULL;
