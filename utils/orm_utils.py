
from tortoise.queryset import Q
import tortoise
import ast

def pagination(limit: int, page: int, count_model: int):
    # limit = 5
    offset = (page - 1) * limit
    # count = await history_balance.count()
    last_page = count_model/limit
    if count_model % limit == 0:
        last_page = int(last_page)
    elif count_model % limit != 0:
        last_page = int(last_page + 1)
    previous_page = page-1
    next_page = page+1
    if page == 1:
        previous_page = None
    if page == last_page:
        next_page = None
    if page > last_page:
        pass
    return offset, last_page, previous_page, next_page


async def rowsql_get_distinct_list_value(find_string: str, table: str):
    conn = tortoise.Tortoise.get_connection("default")
    sql = f'''select t.uuid 
              from (select uuid, jsonb_each_text({table}.data)::text as json_string
                    from {table}) as t
              where LOWER(t.json_string) like '%{find_string.lower()}%'; 
          '''
    return await conn.execute_query_dict(sql)


def order_by_utils(order_by: str):
    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []
    order_by_args = []
    if len(order_by) == 0:
        order_by_args.append("-created_at")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        order_by_args = order_by
    return order_by, order_by_args




async def query_filters(model) -> Q:
    q = Q()
    for k,v in model.__dict__.items():
        if v is not None and k.split('__')[-1] != "json":
            q &= Q(**{k:v})
    return q