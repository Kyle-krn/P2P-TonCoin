INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at) VALUES
	 ('3a47043e-ce4b-4a0e-a83b-53143f5dda55',NULL,NULL,'Выберите валюту, в которой вы хотите купить Toncoin:','Выберите валюту, в которой вы хотите купить Toncoin:','Купить Ton','2022-06-15 15:25:33.216688+03','2022-06-15 15:25:33.216716+03'),
	 ('c8bc4326-82af-406d-8787-b2a461bd6a66',NULL,NULL,'Выберите тип способа оплаты:','Выберите тип способа оплаты:','Купить Ton','2022-06-15 15:26:30.644299+03','2022-06-15 15:26:30.644328+03'),
	 ('ddd66c21-b642-4e39-aebf-57dd80b69eb5',NULL,NULL,'Цена 1 монеты {price_one_coin} {currency}
Общее количество монет, доступное к покупке - {allowed_sum_coin}
Минимальная сумма, на которую доступна покупка - {min_buy_sum} {currency}
Общая стоимость - {full_price} {currency}
Доступные способы оплаты - {allowed_pay_type}
','Цена 1 монеты {price_one_coin} {currency}
Общее количество монет, доступное к покупке - {allowed_sum_coin}
Минимальная сумма, на которую доступна покупка - {min_buy_sum} {currency}
Общая стоимость - {full_price} {currency}
Доступные способы оплаты - {allowed_pay_type}
','Купить Ton','2022-06-15 15:28:08.643038+03','2022-06-15 15:28:08.643066+03'),
	 ('e4ae3df2-f1ce-4003-86c0-36d1fc7028b6',NULL,NULL,'Введите количество Toncoin, которое вы хотите купить(сумма покупки должна быть не меньше {min_buy_sum})','Введите количество Toncoin, которое вы хотите купить(сумма покупки должна быть не меньше {min_buy_sum})','Купить Ton','2022-06-15 15:28:36.488828+03','2022-06-15 15:28:36.488855+03'),
	 ('efeb95c8-46b0-485e-bd44-d27a4b0d633d',NULL,NULL,'Введите количество Toncoin, которое вы хотите купить(сумма покупки должна быть не меньше от {min_buy_sum} {currency} до {full_price} {currency})','Введите количество Toncoin, которое вы хотите купить(сумма покупки должна быть не меньше от {min_buy_sum} {currency} до {full_price} {currency})','Купить Ton','2022-06-15 15:29:40.472589+03','2022-06-15 15:29:40.472619+03'),
	 ('1235401b-7b99-4798-9ea2-82f94e1f46b4',NULL,NULL,'Заказ отменен.','Заказ отменен.','Купить Ton','2022-06-15 15:31:04.596214+03','2022-06-15 15:31:04.596244+03'),
	 ('f1defc4d-e4cc-4afa-be24-5f911a4508bf',NULL,NULL,'По заказу №{uuid} покупатель отправил денежные средства в размере {final_price} {currency}.
Подтвердите получение оплаты, нажав кнопку Я получил средства, либо нажмите Средства не поступили, если деньги не поступили на ваш счет','По заказу №{uuid} покупатель отправил денежные средства в размере {final_price} {currency}.
Подтвердите получение оплаты, нажав кнопку Я получил средства, либо нажмите Средства не поступили, если деньги не поступили на ваш счет','Купить Ton','2022-06-15 15:32:08.392214+03','2022-06-15 15:32:08.392244+03'),
	 ('36243794-383e-4c93-a1c6-fe9a0dafe54a',NULL,NULL,'Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом','Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом','Купить Ton','2022-06-15 15:32:40.622507+03','2022-06-15 15:32:40.622539+03'),
	 ('fa34de05-0e16-421a-b563-b939bd0d89af',NULL,NULL,'Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем.','Деньги могут приходить с задержкой, подождите 5 минут после отправки покупателем.','Купить Ton','2022-06-15 15:33:20.031105+03','2022-06-15 15:33:20.031136+03'),
	 ('9b7fbd7c-ba72-4de8-bb4c-c41c0628cd0b',NULL,NULL,'Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам.','Сейчас мы проверим оплату от покупателя, запросим у него чек и отправим его вам.','Купить Ton','2022-06-15 15:33:38.5751+03','2022-06-15 15:33:38.575129+03');
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at) VALUES
	 ('de220ffc-1210-4433-a681-76c30a829ca7',NULL,NULL,'Кошелёк

Баланс Toncoin: {balance} TON
Заморожено в заказах на продажу Toncoin: {frozen_balance} TON','Кошелёк

Баланс Toncoin: {balance} TON
Заморожено в заказах на продажу Toncoin: {frozen_balance} TON','Кошелек','2022-06-15 15:58:47.263399+03','2022-06-15 15:58:47.263416+03'),
	 ('c8b08b1b-8dfc-484f-a0c5-b106e2958bf5',NULL,NULL,'Используйте адрес ниже для пополнения баланса TON.

Сеть: The Open Network – TON

{address_smart_contract}

ОБЯЗАТЕЛЬНО укажите код <b>{code}</b> в комментарии при пополнении баланса. Без этого кода ваше пополнение баланса может не отразиться в системе','Используйте адрес ниже для пополнения баланса TON.

Сеть: The Open Network – TON

{address_smart_contract}

ОБЯЗАТЕЛЬНО укажите код <b>{code}</b> в комментарии при пополнении баланса. Без этого кода ваше пополнение баланса может не отразиться в системе','Кошелек','2022-06-15 16:00:04.457741+03','2022-06-15 16:00:04.457758+03'),
	 ('34cff16d-6bd5-4eb1-ae12-3655095511fc',NULL,NULL,'Для вывода доступно {permission_balance} TON
Отправьте количество TON, которое вы хотите вывести (не более {permission_balance} TON)','Для вывода доступно {permission_balance} TON
Отправьте количество TON, которое вы хотите вывести (не более {permission_balance} TON)','Кошелек','2022-06-15 16:01:14.881313+03','2022-06-15 16:01:14.88133+03'),
	 ('b18512b1-9e18-4fda-ac00-ab2f45bf323b',NULL,NULL,'Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON','Введите номер кошелька, на который вы хотите вывести {withdraw_amount} TON','Кошелек','2022-06-15 16:03:52.949432+03','2022-06-15 16:03:52.94945+03'),
	 ('ad436ce0-a56a-4022-9222-9fc309b23c82',NULL,NULL,'Вывод средств на сумму {amount} TON успешно выполнен!Ваш баланс: {balance} TON','Вывод средств на сумму {amount} TON успешно выполнен!Ваш баланс: {balance} TON','Кошелек','2022-06-15 16:06:16.30009+03','2022-06-15 16:06:16.300107+03'),
	 ('38cf9afe-083a-4e90-a29c-a743cc6895fa',NULL,NULL,'Выберите ваш способ оплаты для изменения или добавьте новый','Выберите ваш способ оплаты для изменения или добавьте новый','Мои счета','2022-06-15 16:08:49.295601+03','2022-06-15 16:08:49.295618+03'),
	 ('f2bdd4ea-71c6-4d8c-9e2b-1875ebbe7403',NULL,NULL,'Выберите валюту способа оплаты:','Выберите валюту способа оплаты:','Мои счета','2022-06-15 16:10:05.301429+03','2022-06-15 16:10:05.301447+03'),
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
После оплаты нажмите кнопку Я отправил средства','Купить Ton','2022-06-15 15:30:44.95982+03','2022-06-15 15:30:44.95985+03'),
	 ('922417b3-1220-47c1-83ab-df140eda8f19',NULL,NULL,'Продавец сообщил, что не получил оплату от вас.Пришлите, пожалуйста, подтверждение оплаты (чек)в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение.Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен','Продавец сообщил, что не получил оплату от вас.Пришлите, пожалуйста, подтверждение оплаты (чек)в формате pdf / xls / xcls / jpg / pdf / gif в ответ на это сообщение.Если вы не пришлете подтверждение в течение 24 часов, то заказ будет автоматически отменен','Купить Ton','2022-06-15 15:33:58.973668+03','2022-06-15 15:33:58.973695+03'),
	 ('aa66b9f2-8bf6-4d1b-9e8c-207ef6787935',NULL,NULL,'Пополните баланс для создания заказа на продажу TonCoin','Пополните баланс для создания заказа на продажу TonCoin','Продать Ton','2022-06-15 15:44:06.858358+03','2022-06-15 15:44:06.858393+03');
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at) VALUES
	 ('c060e220-26d5-4138-ac3d-edda436a659a',NULL,NULL,'Введите количество TON, которое вы хотите продать (число от 0.1 до {balance})','Введите количество TON, которое вы хотите продать (число от 0.1 до {balance})','Продать Ton','2022-06-15 15:44:36.262567+03','2022-06-15 15:44:36.2626+03'),
	 ('82daaee6-9971-449e-99af-0513ccccf5cc',NULL,NULL,'Неверный формат ввода. Введите число от 0.1 до {balance}','Неверный формат ввода. Введите число от 0.1 до {balance}','Продать Ton','2022-06-15 15:45:01.122596+03','2022-06-15 15:45:01.122625+03'),
	 ('f32f4c20-acae-4017-9be8-daaf71db151c',NULL,NULL,'Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100
Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap','Введите наценку, с которой вы хотите продать TON в процентах от 1 до 100
Стоимость TON в момент продажи рассчитывается онлайн на основе курса CoinMarketCap','Продать Ton','2022-06-15 15:48:23.659929+03','2022-06-15 15:48:23.659958+03'),
	 ('1879a3dd-825f-4a50-97e3-9e62d183dc8c',NULL,NULL,'Неверный формат ввода. Введите число от 1 до 100','Неверный формат ввода. Введите число от 1 до 100','Продать Ton','2022-06-15 15:48:40.743768+03','2022-06-15 15:48:40.743793+03'),
	 ('10efd114-3a48-4bd4-986b-ac8f5ff207b9',NULL,NULL,'Выберите валюту, в которой вы хотите продать TonCoin:','Выберите валюту, в которой вы хотите продать TonCoin:','Продать Ton','2022-06-15 15:49:25.55922+03','2022-06-15 15:49:25.559251+03'),
	 ('04e0b432-a089-473b-9215-562db2af04d1',NULL,NULL,'Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе
Введите число от 1 {currency} до {max_price} {currency}','Введите минимальную сумму, на которую покупатель может купить TON из всего объема TON, продаваемых в заказе
Введите число от 1 {currency} до {max_price} {currency}','Продать Ton','2022-06-15 15:50:15.427421+03','2022-06-15 15:50:15.42744+03'),
	 ('8168939f-31f4-416a-b9e9-896e296f6b34',NULL,NULL,'Создайте хотя бы один аккаунт в выбранной валюте, куда пользователи смогут отправлять вам средства за заказ.','Создайте хотя бы один аккаунт в выбранной валюте, куда пользователи смогут отправлять вам средства за заказ.','Продать Ton','2022-06-15 15:52:52.233203+03','2022-06-15 15:52:52.23322+03'),
	 ('85157487-6f40-4d4f-8544-efb89252ed51',NULL,NULL,'Выберите тип способа оплаты:','Выберите тип способа оплаты:','Продать Ton','2022-06-15 15:55:17.986434+03','2022-06-15 15:55:17.986466+03'),
	 ('0e904051-3033-45a2-9dd5-18199519359d',NULL,NULL,'Выберите тип способа оплаты:','Выберите тип способа оплаты:','Продать Ton','2022-06-15 15:55:27.868034+03','2022-06-15 15:55:27.868061+03'),
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
','Продать Ton','2022-06-15 15:57:00.868735+03','2022-06-15 15:57:00.868768+03');
INSERT INTO public.lang (uuid,target_table,target_id,rus,eng,description,updated_at,created_at) VALUES
	 ('9f1a916e-ffaa-4dfc-9e90-d6935492561c',NULL,NULL,'На вашем балансе нет средств.','На вашем балансе нет средств.','Кошелек','2022-06-15 16:02:53.687425+03','2022-06-15 16:02:53.687442+03'),
	 ('3765be5b-239f-4299-960a-369fd34fef96',NULL,NULL,'Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с вашим реферальным кодов {link}, то вы получите 1 Toncoin на ваш счет','Пришлите ссылку на этот бот своему другу, и, если он зарегестрируется с вашим реферальным кодов {link}, то вы получите 1 Toncoin на ваш счет','Рефералка','2022-06-15 16:08:08.371076+03','2022-06-15 16:08:08.371094+03'),
	 ('50407743-511d-4f95-bad9-36dc5e69e433',NULL,NULL,'Валюта: {cur_name}
Тип оплаты: {type_name}
{user_data_text}','Валюта: {cur_name}
Тип оплаты: {type_name}
{user_data_text}','Мои счета','2022-06-15 16:09:31.758807+03','2022-06-15 16:09:31.758826+03'),
	 ('f11ebe57-866f-4bd3-8550-690fa288dd9f',NULL,NULL,'Выберите заказ:','Выберите заказ:',NULL,'2022-06-15 16:14:06.846447+03','2022-06-15 16:14:06.846465+03'),
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
',NULL,'2022-06-15 16:15:39.209559+03','2022-06-15 16:15:39.209575+03'),
	 ('56a300c4-ee27-4619-8112-c98c10bfdaec',NULL,NULL,'Ваш заказ № {order_uuid} отменен!
Мы вернули вам {order_amount} TON ваш кошелек
Будем ждать вас снова!
','Ваш заказ № {order_uuid} отменен!
Мы вернули вам {order_amount} TON ваш кошелек
Будем ждать вас снова!
',NULL,'2022-06-15 16:16:17.173139+03','2022-06-15 16:16:17.173156+03');