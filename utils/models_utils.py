from tortoise.queryset import Q

async def query_filters(model):
    q = Q()
    for k,v in model.__dict__.items():
        
        if v is not None and k.split('__')[-1] != "json":
            print({k:v})
            q &= Q(**{k:v})
    return q