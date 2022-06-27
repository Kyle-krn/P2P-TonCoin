-- upgrade --
ALTER TABLE "order_amount_change" ALTER COLUMN "target_order_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "order_amount_change" ALTER COLUMN "target_order_id" SET NOT NULL;
