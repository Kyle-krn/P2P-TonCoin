from uuid import UUID
from fastapi import APIRouter, Depends, Request
from loader import templates, manager, bot
from models import models
from fastapi.responses import RedirectResponse
from starlette import status
from ..forms import UpdateOrderStateForm
from utils import orm_utils
from utils.lang import lang_text

change_state_roter = APIRouter()

@change_state_roter.get("/change_state_order/{uuid}")
async def show_change_state_order(request: Request,
                             uuid: UUID,
                             page: int = 1,
                             staff: models.Staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid).prefetch_related("seller", "customer", "currency", "children_order")
    change_state_list = models.OrderStateChange.filter(order=order)
    limit = 30
    offset, last_page, previous_page, next_page = orm_utils.pagination(limit=limit, page=page, count_model=await change_state_list.count())
    change_state_list = await change_state_list.offset(offset).limit(limit).order_by("-created_at").prefetch_related("staff")
    context = {'request': request,
               'params': request.query_params._dict,
               "order": order,
               "proof": await order.proof_problem_order.all().first(),
               "order_change_state": change_state_list,
               "page": page,
               "last_page": last_page,
               "previous_page": previous_page,
               "next_page": next_page,
               "pagination_url": f"/change_state_order/{uuid}",}
    return templates.TemplateResponse("orders/order_change_state.html", context)



@change_state_roter.post("/update_state_order/{uuid}")
async def update_state_order(request: Request,
                             uuid: UUID,
                             staff = Depends(manager)):
    order = await models.Order.get(uuid=uuid)
    form = UpdateOrderStateForm(request)
    await form.load_data()
    if form.is_valid():
        if order.state != form.state:
            await models.OrderStateChange.create(order=order, old_state=order.state, new_state=form.state, staff=staff, description=form.description)
            order.state = form.state
            await order.save()
    else:
        form.flash_error()
    return RedirectResponse(request.url_for("show_change_state_order", uuid=order.uuid), status_code=status.HTTP_302_FOUND)


@change_state_roter.get("/order_admin_resolution/{action}/{order_uuid}")
@change_state_roter.get("/order_admin_resolution/{action}/{order_uuid}")
async def order_admin_resolution(request: Request,
                                 action: str,
                                 order_uuid: UUID,
                                 staff = Depends(manager)):
    order = await models.Order.get(uuid=order_uuid)
    seller = await order.seller
    customer = await order.customer
    payment_operation = await order.payment_operation.all().first()
    if action == "approve":
        customer.balance += (order.amount - order.commission)
        seller.frozen_balance -= order.amount
        await models.OrderStateChange.create(order=order, old_state=order.state, new_state="done")
        order.state = "done"
        payment_operation.state = "success"
        await payment_operation.save()
        await order.save()
        await seller.save()
        await customer.save()

        seller_text = await lang_text(lang_uuid="ed54a829-160a-4099-9162-a7fe391e2457",
                                      user=seller,
                                      format={"order_id": order.serial_int})

        # seller_text = "Ваш заказ завершен! Спасибо, что пользуетесь нашим ботом"
        customer_text = await lang_text(lang_uuid="02d0faf7-fc2f-420c-bac4-d7642546b903",
                                        user=customer,
                                        format={
                                                "uuid":order.serial_int, 
                                                "balance":customer.balance
                                        })
        # customer_text = f"Продавец подтвердил получение ваших денежных средств по заказу № {order.uuid} TON отправлены на ваш кошелек"  \
        #                 f"Ваш баланс: {customer.balance} TON"

        await bot.send_message(seller.telegram_id, text=seller_text)
        await bot.send_message(customer.telegram_id, text=customer_text)
    elif action == "reject":
        await models.OrderStateChange.create(order=order, old_state=order.state, new_state="ready_for_sale")
        order.state = "ready_for_sale"
        payment_operation.state = "cancelled"
        order.customer = None
        await order.save()
        await payment_operation.save()
        customer_text = await lang_text(lang_uuid="11b721ba-e9ca-422f-a4eb-972bde4e7556",
                                      user=seller,
                                      format={"order_id": order.serial_int})

        
        seller_text = await lang_text(lang_uuid="9368c84f-8ce6-46df-8638-91d7a515cc2b",
                                        user=customer,
                                        format={"order_id": order.serial_int})
        # customer_text = f"Продавец подтвердил получение ваших денежных средств по заказу № {order.uuid} TON отправлены на ваш кошелек"  \
        #                 f"Ваш баланс: {customer.balance} TON"

        await bot.send_message(seller.telegram_id, text=seller_text)
        await bot.send_message(customer.telegram_id, text=customer_text)
        
    orders = await models.Order.filter(state="suspended", seller_id=seller.uuid)
    
    for order in orders:
        await models.OrderStateChange.create(order=order, 
                                             old_state=order.state, 
                                             new_state="ready_for_sale")
        order.state = "ready_for_sale"
        await order.save()

    
    return RedirectResponse(request.url_for("order_detail", uuid=order_uuid))


