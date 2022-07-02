from tortoise.queryset import Q

async def query_filters(model) -> Q:
    q = Q()
    for k,v in model.__dict__.items():
        # print({k:v})
        if v is not None and k.split('__')[-1] != "json":
            q &= Q(**{k:v})
    return q