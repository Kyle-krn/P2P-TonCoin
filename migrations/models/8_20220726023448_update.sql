-- upgrade --
ALTER TABLE "user_balance_change" ALTER COLUMN "user_id" DROP NOT NULL;
-- downgrade --
ALTER TABLE "user_balance_change" ALTER COLUMN "user_id" SET NOT NULL;
