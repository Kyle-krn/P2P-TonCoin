import ast


def order_by_utils(order_by: str):
    if order_by:
        order_by = ast.literal_eval(order_by)
    else:
        order_by = []

    order_by_args = []

    if len(order_by) == 0:
        # orders = orders.order_by("-created_at")
        order_by_args.append("-created_at")
    else:
        for item in order_by:
            if item[0] == "+":
                indx = order_by.index(item)
                order_by = order_by[:indx] + [item[1:]] + order_by[indx+1:]
        order_by_args = order_by
    return order_by, order_by_args