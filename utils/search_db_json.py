from tortoise import Tortoise


async def rowsql_get_distinct_list_value(find_string: str, table: str):
    conn = Tortoise.get_connection("default")
    sql = f'''select t.uuid 
              from (select uuid, jsonb_each_text({table}.data)::text as json_string
                    from {table}) as t
              where LOWER(t.json_string) like '%{find_string.lower()}%'; 
          '''
    return await conn.execute_query_dict(sql)

