from tortoise import Tortoise


async def rowsql_get_distinct_list_value(find_string: str):
    conn = Tortoise.get_connection("default")
    sql = f'''select t.uuid 
              from (select uuid, jsonb_each_text(user_payment_account.data)::text as json_string
                    from user_payment_account) as t
              where t.json_string like '%{find_string}%'; 
          '''
    return await conn.execute_query_dict(sql)

