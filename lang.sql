INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('3a47043e-ce4b-4a0e-a83b-53143f5dda55',NULL,NULL,'Выберите валюту, в которой вы хотите купить Toncoin:','Выберите валюту, в которой вы хотите купить Toncoin:','Купить Ton','2022-06-15 15:25:33.216688+03','2022-06-15 15:25:33.216716+03',false),
	 ('c8bc4326-82af-406d-8787-b2a461bd6a66',NULL,NULL,'Выберите тип способа оплаты:','Выберите тип способа оплаты:','Купить Ton','2022-06-15 15:26:30.644299+03','2022-06-15 15:26:30.644328+03',false),
	 ('953216e7-3945-490e-bd71-8aab610857f6',NULL,NULL,'Добавить способ оплаты','Add payment method','Мои счета/Продать ','2022-07-01 01:31:38.060611+03','2022-07-01 01:31:38.060611+03',true),
	 ('591918f9-63db-4a54-8912-458368c29113',NULL,NULL,'Данный заказ к сожалению сейчас не доступен.','Данный заказ к сожалению сейчас не доступен.','Купить Ton','2022-07-06 03:09:24.80845+03','2022-07-06 03:09:24.80845+03',false),
	 ('efeb95c8-46b0-485e-bd44-d27a4b0d633d',NULL,NULL,'Введите количество Toncoin, которое вы хотите купить(сумма покупки должна быть не меньше от {min_buy_sum} {currency} до {full_price} {currency})','Введите количество Toncoin, которое вы хотите купить(сумма покупки должна быть не меньше от {min_buy_sum} {currency} до {full_price} {currency})','Купить Ton','2022-06-15 15:29:40.472589+03','2022-06-15 15:29:40.472619+03',false),
	 ('1235401b-7b99-4798-9ea2-82f94e1f46b4',NULL,NULL,'Заказ отменен.','Заказ отменен.','Купить Ton','2022-06-15 15:31:04.596214+03','2022-06-15 15:31:04.596244+03',false),
	 ('f1defc4d-e4cc-4afa-be24-5f911a4508bf',NULL,NULL,'По заказу №{uuid} покупатель отправил денежные средства в размере {final_price} {currency}.
Подтвердите получение оплаты, нажав кнопку Я получил средства, либо нажмите Средства не поступили, если деньги не поступили на ваш счет','По заказу №{uuid} покупатель отправил денежные средства в размере {final_price} {currency}.
Подтвердите получение оплаты, нажав кнопку Я получил средства, либо нажмите Средства не поступили, если деньги не поступили на ваш счет','Купить Ton','2022-06-15 15:32:08.392214+03','2022-06-15 15:32:08.392244+03',false),
	 ('36243794-383e-4c93-a1c6-fe9a0dafe54a',NULL,NULL,'Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом','Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом','Купить Ton','2022-06-15 15:32:40.622507+03','2022-06-15 15:32:40.622539+03',false),
	 ('fa34de05-0e16-421a-b563-b939bd0d89af',NULL,NULL,'Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем.','Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем.','Купить Ton','2022-06-15 15:33:20.031105+03','2022-06-15 15:33:20.031136+03',false),
	 ('9b7fbd7c-ba72-4de8-bb4c-c41c0628cd0b',NULL,NULL,'Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам.','Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам.','Купить Ton','2022-06-15 15:33:38.5751+03','2022-06-15 15:33:38.575129+03',false);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('de220ffc-1210-4433-a681-76c30a829ca7',NULL,NULL,'Кошелёк

Баланс Toncoin: {balance} TON
Заморожено в заказах на продажу Toncoin: {frozen_balance} TON','Кошелёк

Баланс Toncoin: {balance} TON
Заморожено в заказах на продажу Toncoin: {frozen_balance} TON','Кошелек','2022-06-15 15:58:47.263399+03','2022-06-15 15:58:47.263416+03',false),
	 ('c8b08b1b-8dfc-484f-a0c5-b106e2958bf5',NULL,NULL,'Используйте адрес ниже для пополнения баланса TON.

Сеть: The Open Network – TON

{address_smart_contract}

ОБЯЗАТЕЛЬНО укажите код <b>{code}</b> в комментарии при пополнении баланса. Без этого кода ваше пополнение баланса может не отразиться в системе','Используйте адрес ниже для пополнения баланса TON.

Сеть: The Open Network – TON

{address_smart_contract}

ОБЯЗАТЕЛЬНО укажите код <b>{code}</b> в комментарии при пополнении баланса. Без этого кода ваше пополнение баланса может не отразиться в системе','Кошелек','2022-06-15 16:00:04.457741+03','2022-06-15 16:00:04.457758+03',false),
	 ('34cff16d-6bd5-4eb1-ae12-3655095511fc',NULL,NULL,'Для вывода доступно {permission_balance} TON
Отправьте количество TON, которое вы хотите вывести (не более {permission_balance} TON)','Для вывода доступно {permission_balance} TON
Отправьте количество TON, которое вы хотите вывести (не более {permission_balance} TON)','Кошелек','2022-06-15 16:01:14.881313+03','2022-06-15 16:01:14.88133+03',false),
	 ('b18512b1-9e18-4fda-ac00-ab2f45bf323b',NULL,NULL,'Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON','Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON','Кошелек','2022-06-15 16:03:52.949432+03','2022-06-15 16:03:52.94945+03',false),
	 ('ad436ce0-a56a-4022-9222-9fc309b23c82',NULL,NULL,'Вывод средств на сумму {amount} TON успешно выполнен!Ваш баланс: {balance} TON','Вывод средств на сумму {amount} TON успешно выполнен!Ваш баланс: {balance} TON','Кошелек','2022-06-15 16:06:16.30009+03','2022-06-15 16:06:16.300107+03',false),
	 ('38cf9afe-083a-4e90-a29c-a743cc6895fa',NULL,NULL,'Выберите ваш способ оплаты для изменения или добавьте новый','Выберите ваш способ оплаты для изменения или добавьте новый','Мои счета','2022-06-15 16:08:49.295601+03','2022-06-15 16:08:49.295618+03',false),
	 ('f2bdd4ea-71c6-4d8c-9e2b-1875ebbe7403',NULL,NULL,'Выберите валюту способа оплаты:','Выберите валюту способа оплаты:','Мои счета','2022-06-15 16:10:05.301429+03','2022-06-15 16:10:05.301447+03',false),
	 ('04e0b432-a089-473b-9215-562db2af04d1',NULL,NULL,'Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе
Введите число от 0.01 {currency} до {max_price} {currency}','Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе
Введите число от 1 {currency} до {max_price} {currency}','Продать Ton','2022-06-15 15:50:15.427421+03','2022-06-15 15:50:15.42744+03',false),
	 ('9afbc187-ca12-4ff6-8f65-67b49c66b222',NULL,NULL,'Вы имеете не завершенную сделку.','Вы имеете не завершенную сделку.','Купить Ton','2022-07-06 03:10:14.688677+03','2022-07-06 03:10:14.688677+03',false),
	 ('73323c38-3f22-48db-8da6-fe31fba72ef0',NULL,NULL,'Ожидайте ответа от продавца.','Ожидайте ответа от продавца.','Купить Ton','2022-07-06 03:18:15.665262+03','2022-07-06 03:18:15.665262+03',false);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('bd9ce42c-6fab-4bb3-981a-bdf4a402f722',NULL,NULL,'Не подходит state','Не подходит state','Купить Ton','2022-07-06 03:28:52.69002+03','2022-07-06 03:28:52.69002+03',false),
	 ('bd7b7e0d-2420-4914-87cd-7462d9b07697',NULL,NULL,'Нельзя отменить заказ','Нельзя отменить заказ','Сделки','2022-07-06 03:28:52.691705+03','2022-07-06 03:28:52.691705+03',false),
	 ('53d85fb5-bcf9-4ff0-ad98-3326bc02c3e7',NULL,NULL,'Нельзя добавить платежные аккаунты в этот заказ.','Нельзя добавить платежные аккаунты в этот заказ.','Сделки','2022-07-06 03:29:57.891129+03','2022-07-06 03:29:57.891129+03',false),
	 ('854b6bd4-0147-4ee1-9293-85eefaf34f90',NULL,NULL,'У вас 15 минут для завершение заказа.
Этапы совершения заказа:
вы перечисляете деньги продавцу
мы отправляем вам TON на ваш кошелек в системе

Отправьте {final_price} {currency} по следующим реквизитам:
{user_data_text}
Вы получите {amount} TON
После оплаты нажмите кнопку Я отправил средства','У вас 15 минут для завершение заказа.
Этапы совершения заказа:
вы перечисляете деньги продавцу
мы отправляем вам TON на ваш кошелек в системе

Отправьте {final_price} {currency} по следующим реквизитам:
{user_data_text}
Вы получите {amount} TON
После оплаты нажмите кнопку Я отправил средства','Купить Ton','2022-06-15 15:30:44.95982+03','2022-06-15 15:30:44.95985+03',false),
	 ('922417b3-1220-47c1-83ab-df140eda8f19',NULL,NULL,'Продавец сообщил, что не получил оплату от вас.Пришлите, пожалуйста, подтверждение оплаты (чек)в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение.Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен','Продавец сообщил, что не получил оплату от вас.Пришлите, пожалуйста, подтверждение оплаты (чек)в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение.Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен','Купить Ton','2022-06-15 15:33:58.973668+03','2022-06-15 15:33:58.973695+03',false),
	 ('aa66b9f2-8bf6-4d1b-9e8c-207ef6787935',NULL,NULL,'Пополните баланс для создания заказа на продажу TonCoin','Пополните баланс для создания заказа на продажу TonCoin','Продать Ton','2022-06-15 15:44:06.858358+03','2022-06-15 15:44:06.858393+03',false),
	 ('c060e220-26d5-4138-ac3d-edda436a659a',NULL,NULL,'Введите количество TON, которое вы хотите продать (число от 0.1 до {balance})','Введите количество TON, которое вы хотите продать (число от 0.1 до {balance})','Продать Ton','2022-06-15 15:44:36.262567+03','2022-06-15 15:44:36.2626+03',false),
	 ('82daaee6-9971-449e-99af-0513ccccf5cc',NULL,NULL,'Неверный формат ввода. Введите число от 0.1 до {balance}','Неверный формат ввода. Введите число от 0.1 до {balance}','Продать Ton','2022-06-15 15:45:01.122596+03','2022-06-15 15:45:01.122625+03',false),
	 ('f32f4c20-acae-4017-9be8-daaf71db151c',NULL,NULL,'Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100
Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap','Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100
Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap','Продать Ton','2022-06-15 15:48:23.659929+03','2022-06-15 15:48:23.659958+03',false),
	 ('a71cd1a0-5624-454d-9213-850196ea13b6',NULL,NULL,'Внести средства','Deposit funds','Сделки','2022-07-01 01:25:32.514341+03','2022-07-01 01:25:32.514341+03',true);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('10efd114-3a48-4bd4-986b-ac8f5ff207b9',NULL,NULL,'Выберите валюту, в которой вы хотите продать TonCoin:','Выберите валюту, в которой вы хотите продать TonCoin:','Продать Ton','2022-06-15 15:49:25.55922+03','2022-06-15 15:49:25.559251+03',false),
	 ('0810c546-5062-45b0-944c-818ab8c58ef8',NULL,NULL,'Изменить данные','Change data',NULL,'2022-07-01 01:53:08.134138+03','2022-07-01 01:53:08.134138+03',true),
	 ('8168939f-31f4-416a-b9e9-896e296f6b34',NULL,NULL,'Создайте хотя бы один аккаунт в выбранной валюте, куда пользователи смогут отправлять вам средства за заказ.','Создайте хотя бы один аккаунт в выбранной валюте, куда пользователи смогут отправлять вам средства за заказ.','Продать Ton','2022-06-15 15:52:52.233203+03','2022-06-15 15:52:52.23322+03',false),
	 ('589a40cc-279f-40b2-a706-2f331fbf2723',NULL,NULL,'Удалить способ оплаты','Remove payment method',NULL,'2022-07-01 01:53:08.136771+03','2022-07-01 01:53:08.136771+03',true),
	 ('ee766ac7-47f1-47be-b5eb-f8f3a8c2fcd6',NULL,NULL,'Отправь ссылку другу','Отправь ссылку другу',NULL,'2022-07-01 01:53:08.138694+03','2022-07-01 01:53:08.138694+03',true),
	 ('697085d7-ebfd-4756-9425-7f0b160b41af',NULL,NULL,'Ваш заказ № {order_uuid} успешно опубликован.
Комиссия за продажу равна 1% в TonCoin
Таким образом финальное количество продаваемых TonCoin равно {order_amount}
Как только покупатель будет найден, мы отправим вам сообщение.
Если вы хотите отменить заказ, можете сделать это в интерфейсе Мои заказы
','Ваш заказ № {order_uuid} успешно опубликован.
Комиссия за продажу равна 1% в TonCoin
Таким образом финальное количество продаваемых TonCoin равно {order_amount}
Как только покупатель будет найден, мы отправим вам сообщение.
Если вы хотите отменить заказ, можете сделать это в интерфейсе Мои заказы
','Продать Ton','2022-06-15 15:57:00.868735+03','2022-06-15 15:57:00.868768+03',false),
	 ('9f1a916e-ffaa-4dfc-9e90-d6935492561c',NULL,NULL,'На вашем балансе нет средств.','На вашем балансе нет средств.','Кошелек','2022-06-15 16:02:53.687425+03','2022-06-15 16:02:53.687442+03',false),
	 ('3765be5b-239f-4299-960a-369fd34fef96',NULL,NULL,'Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с вашим реферальным кодов {link}, то вы получите 1 Toncoin на ваш счет','Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с вашим реферальным кодов {link}, то вы получите 1 Toncoin на ваш счет','Рефералка','2022-06-15 16:08:08.371076+03','2022-06-15 16:08:08.371094+03',false),
	 ('1879a3dd-825f-4a50-97e3-9e62d183dc8c',NULL,NULL,'Неверный формат ввода. Введите число от 0.01 до 100','Неверный формат ввода. Введите число от 1 до 100','Продать Ton','2022-06-15 15:48:40.743768+03','2022-06-15 15:48:40.743793+03',false),
	 ('f4059557-00c3-45fe-81d8-8d132dc16698',NULL,NULL,'Успешно удалено','Успешно удалено','Платежные аккаунты','2022-07-06 03:38:58.419172+03','2022-07-06 03:38:58.419172+03',false);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('f11ebe57-866f-4bd3-8550-690fa288dd9f',NULL,NULL,'Выберите заказ:','Выберите заказ:','None','2022-07-11 22:56:27.815112+03','2022-06-15 16:14:06.846465+03',false),
	 ('50407743-511d-4f95-bad9-36dc5e69e433',NULL,NULL,'Валюта: {cur_name}
Тип оплаты: {type_name}
{user_data_text}','Валюта: {cur_name}
Тип оплаты: {type_name}
{user_data_text}','Мои счета','2022-07-11 22:56:27.820211+03','2022-06-15 16:09:31.758826+03',false),
	 ('e3098392-83e7-4a0e-a8c1-6a44741d7894',NULL,NULL,'Выберите способы оплаты, которые доступны для этого заказа, или создайте новый','Выберите способы оплаты, которые доступны для этого заказа, или создайте новый','Продать Ton','2022-06-15 16:45:52.264658+03','2022-06-15 16:45:52.264687+03',false),
	 ('ecc46c6b-90d1-45c3-be85-a3eace3b93f2',NULL,NULL,'Добро пожаловать в официальный бот для p2p обмена Toncoin. Выберите язык, на котором вам удобно работать:','Добро пожаловать в официальный бот для p2p обмена Toncoin.\n Выберите язык, на котором вам удобно работать:','start','2022-06-29 20:22:36.345298+03','2022-06-29 20:22:36.345298+03',false),
	 ('67beaccf-d10f-4c0d-9c6f-6d4f476dedb5',NULL,NULL,'Ожидает оплату от покупателя','Wait money for buy','Стейт сделки','2022-07-01 00:09:11.715202+03','2022-07-01 00:09:11.715202+03',true),
	 ('2615be7e-9735-4563-a97e-c003076d3bc6',NULL,NULL,'Русский','Russian','Выбор языка','2022-06-29 22:16:06.950377+03','2022-06-29 22:16:06.950377+03',true),
	 ('f82068f9-63c5-4c36-96b7-c5c5aa781a09',NULL,NULL,'Добро пожаловать в официальный бот для p2p обмена Toncoin.','Добро пожаловать в официальный бот для p2p обмена Toncoin.','start','2022-06-29 20:22:36.383543+03','2022-06-29 20:22:36.383543+03',false),
	 ('419722a1-70a0-430a-a2e0-033f17245ba0',NULL,NULL,'Спасибо! Мы инициировали разбирательство по заказу. В течение 24 часов вы получите ответ','Спасибо! Мы инициировали разбирательство по заказу. В течение 24 часов вы получите ответ','proof','2022-06-29 20:26:48.038913+03','2022-06-29 20:26:48.038913+03',false),
	 ('cb5de656-c423-4e0c-a5a7-e8c07b3891ce',NULL,NULL,'Неверный формат подтверждения оплаты. Пришлите, пожалуйста, подтверждение оплаты (чек) в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение. Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен.','Неверный формат подтверждения оплаты. Пришлите, пожалуйста, подтверждение оплаты (чек) в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение. Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен.','proof','2022-06-29 20:25:19.051095+03','2022-06-29 20:25:19.051095+03',false),
	 ('69acb044-36b4-4b22-bdcf-a5bb6b1071aa',NULL,NULL,'Пополнить','Top up','Кошелек','2022-06-29 22:22:40.715879+03','2022-06-29 22:22:40.715879+03',true);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('3fc4161c-c306-4376-997b-b8929f699922',NULL,NULL,'Английский','English','Выбор языка','2022-06-29 22:19:10.246784+03','2022-06-29 22:19:10.246784+03',true),
	 ('075ef4c1-8995-42d6-bde1-3f8c2e89da9e',NULL,NULL,'Вывести','Withdraw','Кошелек','2022-06-29 22:23:34.831522+03','2022-06-29 22:23:34.831522+03',true),
	 ('c116ece4-f278-4c91-a9af-b6c679803f20',NULL,NULL,'Отмена','Cancel','Отмена ввода данных','2022-06-30 14:23:09.615869+03','2022-06-30 14:23:09.615869+03',true),
	 ('eef933b0-e3bc-46ed-8461-8226fd5f090f',NULL,NULL,'Назад','Back','Общее','2022-06-30 16:24:48.567923+03','2022-06-30 16:24:48.567923+03',true),
	 ('714f9df6-1b0a-446b-a462-cbaa2e8fe19d',NULL,NULL,'Выбрать все','Select all','Продать монеты','2022-06-30 16:27:11.609815+03','2022-06-30 16:27:11.609815+03',true),
	 ('4ed8b02d-8577-42f3-8a85-67939b608fc6',NULL,NULL,'Перейти к сделке','Go to deals',NULL,'2022-06-30 16:37:16.561438+03','2022-06-30 16:37:16.561438+03',true),
	 ('60a740c2-88f9-488a-8579-cb1fa2b1451a',NULL,NULL,'Купить','Buy',NULL,'2022-06-30 16:48:45.844079+03','2022-06-30 16:48:45.844079+03',true),
	 ('e1103afb-accd-472d-a707-1c5c70e55fe0',NULL,NULL,'Отменить','Cancel',NULL,'2022-06-30 16:48:45.856547+03','2022-06-30 16:48:45.856547+03',true),
	 ('778b75ff-0580-49d9-8b48-d41eb858bf59',NULL,NULL,'Я отправил средства','I send money',NULL,'2022-06-30 16:48:45.859586+03','2022-06-30 16:48:45.859586+03',true),
	 ('d948631c-e9c3-44f1-9445-0ff1497b0ac0',NULL,NULL,'Я получил средства','I get money',NULL,'2022-06-30 16:48:45.863554+03','2022-06-30 16:48:45.863554+03',true);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('76c4e43e-b207-4e33-8360-605de01080b5',NULL,NULL,'Средства не поступили','I not get money',NULL,'2022-06-30 16:48:45.867288+03','2022-06-30 16:48:45.867288+03',true),
	 ('e8f93b03-16f6-4675-94e1-9e36c66ce943',NULL,NULL,'Создано','Created','Стейт сделки','2022-06-30 23:46:02.204944+03','2022-06-30 23:46:02.204944+03',true),
	 ('4aa099f5-06c5-4400-9ff4-63afd0688202',NULL,NULL,'Ожидает покупателя','Wait buyer','Стейт сделки','2022-07-01 00:04:16.014762+03','2022-07-01 00:04:16.014762+03',true),
	 ('4edb3d5a-bfc6-4834-94a6-81d0e0b41207',NULL,NULL,'Ожидает подтверждения средств на ваш счет','Waiting for confirmation of funds to your account','Стейт сделки','2022-07-01 00:11:15.420417+03','2022-07-01 00:11:15.420417+03',true),
	 ('3fe0644c-af1e-466c-bad9-0c53e1fd84ef',NULL,NULL,'Проблема с поступлением средств','Funding problem','Стейт сделки','2022-07-01 01:14:52.176412+03','2022-07-01 01:14:52.176412+03',true),
	 ('3989b0e3-0631-4429-bd99-3fbac9a59b3a',NULL,NULL,'Ожидает решения администрации','Awaiting management decision','Стейт сделки','2022-07-01 01:14:52.179336+03','2022-07-01 01:14:52.179336+03',true),
	 ('f49402b2-f81a-4daa-9181-5031f435b8aa',NULL,NULL,'⬅️','⬅️','Пагинация','2022-07-01 01:14:52.181562+03','2022-07-01 01:14:52.181562+03',true),
	 ('6d821da8-34f1-410b-8df6-aa1c7447ef5a',NULL,NULL,'{page}/{last_page}📄','{page}/{last_page}📄','Пагинация','2022-07-01 01:16:04.998562+03','2022-07-01 01:16:04.998562+03',true),
	 ('4ba02a78-90a7-4a71-9c21-292098e1456c',NULL,NULL,'➡️','➡️','Пагинация','2022-07-01 01:19:41.768157+03','2022-07-01 01:19:41.768157+03',true),
	 ('93a3e2ea-a462-462a-8fca-a3689d3d0690',NULL,NULL,'Вы выбрали: {cur_name}','Вы выбрали: {cur_name}','Продать Ton','2022-07-06 01:45:27.254694+03','2022-07-06 01:45:27.254694+03',false);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('e0806c13-daba-4a79-a95e-97705c3090fb',NULL,NULL,'Выберите язык:','Change language:','None','2022-07-11 22:56:27.79019+03','2022-06-29 20:53:52.776748+03',false),
	 ('8a33cc94-7dff-468a-bdaa-2bfef60406b2',NULL,NULL,'Введите {payment_type_data_value}:','Введите {payment_type_data_value}:','None','2022-07-11 22:56:27.803647+03','2022-06-15 16:30:47.141342+03',false),
	 ('f77f9194-9387-443c-82b4-9755648ef91f',NULL,NULL,'Ваш запрос зарегистрирован, мы пришлем сообщение, когда вывод будет осуществлен','Ваш запрос зарегистрирован, мы пришлем сообщение, когда вывод будет осуществлен','None','2022-07-12 15:53:14.930415+03','2022-07-12 14:27:40.956783+03',false),
	 ('b620cad0-5c97-4752-9d44-20ff6d622b10',NULL,NULL,'К сожалению в данный момент нет объявлений о продаже','К сожалению в данный момент нет объявлений о продаже','None','2022-07-11 22:56:27.75336+03','2022-07-10 01:14:27.969631+03',false),
	 ('8b158613-f1dc-4aa0-bbf0-3a4cbfce692c',NULL,NULL,'Нет активных заказов','Нет активных заказов','None','2022-07-11 22:56:27.758133+03','2022-07-10 00:09:32.935496+03',false),
	 ('9aee8627-5946-466c-bf64-231d4170c34f',NULL,NULL,'Выберите тип способа оплаты:','Выберите тип способа оплаты:','None','2022-07-11 22:56:27.762981+03','2022-07-09 23:06:48.434771+03',false),
	 ('bd8a275e-e8f5-4268-8186-5da5a3cd4bd9',NULL,NULL,'Нет достпуных платежных типов','Нет достпуных платежных типов','None','2022-07-11 22:56:27.766001+03','2022-07-09 22:53:27.698372+03',false),
	 ('b9d67810-9adf-4ae4-99b3-ca9e42225396',NULL,NULL,'Нет доступных валют','Нет доступных валют','None','2022-07-11 22:56:27.769236+03','2022-07-09 22:46:08.345713+03',false),
	 ('743374c9-84e8-4336-a8e9-49b1e70b7b68',NULL,NULL,'По вашей ссылке зарегались, ваш баланс пополнен на {amount} Ton','о вашей ссылке зарегались, ваш баланс пополнен на {amount} Ton','None','2022-07-12 15:53:14.936632+03','2022-07-11 22:09:52.151907+03',false),
	 ('56a300c4-ee27-4619-8112-c98c10bfdaec',NULL,NULL,'Ваш заказ № {order_uuid} отменен!
Мы вернули вам {order_amount} TON ваш кошелек
Будем ждать вас снова!
','Ваш заказ № {order_uuid} отменен!
Мы вернули вам {order_amount} TON ваш кошелек
Будем ждать вас снова!
','None','2022-07-11 22:56:27.807584+03','2022-06-15 16:16:17.173156+03',false);
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at,button) VALUES
	 ('fbddd2d5-a3cd-4a70-95a3-e0128da7c9b7',NULL,NULL,'Цена 1 монеты {price_one_coin} {currency}
Общее количество монет, доступное к покупке - {allowed_sum_coin} TON
Минимальная сумма, на которую доступна покупка - {min_buy_sum} {currency}
Общая стоимость - {full_price} {currency}
Доступные способы оплаты - {allowed_pay_type}
','Цена 1 монеты {price_one_coin} {currency}
Общее количество монет, доступное к покупке - {allowed_sum_coin} TON
Минимальная сумма, на которую доступна покупка - {min_buy_sum} {currency}
Общая стоимость - {full_price} {currency}
Доступные способы оплаты - {allowed_pay_type}
','None','2022-07-11 22:56:27.8119+03','2022-06-15 16:15:39.209575+03',false),
	 ('9055c931-a16b-4fb6-80c6-04d983cbae03',NULL,NULL,'Вывод средств на сумму {amount} TON отклонен!Ваш баланс: {balance} TON','Вывод средств на сумму {amount} TON отклонен!Ваш баланс: {balance} TON','None','2022-07-12 22:35:00.847831+03','2022-07-12 15:40:22.602103+03',false),
	 ('02d0faf7-fc2f-420c-bac4-d7642546b903',NULL,NULL,'Продавец подтвердил получение ваших денежных средств по заказу № {uuid} TON отправлены на ваш кошелек Ваш {balance} TON
','Продавец подтвердил получение ваших денежных средств по заказу № {order.uuid} TON отправлены на ваш кошелек Ваш баланс: {customer.balance} TON
','None','2022-07-11 22:56:27.77336+03','2022-07-06 18:28:21.159499+03',false);