-- upgrade --
ALTER TABLE "order" ADD "customer_pay_type_id" UUID;
ALTER TABLE "order" ADD CONSTRAINT "fk_order_user_pay_c087f133" FOREIGN KEY ("customer_pay_type_id") REFERENCES "user_payment_account_type" ("uuid") ON DELETE CASCADE;
-- downgrade --
ALTER TABLE "order" DROP CONSTRAINT "fk_order_user_pay_c087f133";
ALTER TABLE "order" DROP COLUMN "customer_pay_type_id";
