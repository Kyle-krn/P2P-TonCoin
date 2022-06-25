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