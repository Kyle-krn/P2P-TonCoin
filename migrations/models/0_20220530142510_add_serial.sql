-- upgrade --
ALTER TABLE "user_payment_account_type" ADD "serial_int" SERIAL;
ALTER TABLE "user_payment_account" ADD "serial_int" SERIAL;
-- downgrade --
ALTER TABLE "user_payment_account_type" DROP COLUMN "serial_int";
ALTER TABLE "user_payment_account" ADD COLUMN "serial_int";
