-- upgrade --
ALTER TABLE "user_payment_account_type" DROP COLUMN "serial_int";
ALTER TABLE "user_payment_account" DROP COLUMN "serial_int";
-- downgrade --
ALTER TABLE "user_payment_account_type" ADD "serial_int" INT NOT NULL;
ALTER TABLE "user_payment_account" ADD "serial_int" INT NOT NULL;
