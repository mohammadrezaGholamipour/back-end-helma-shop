from app.models.customer_profile import CustomerProfile
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.order import OrderCreate, OrderOut
from app.models.order import Order, OrderStatus
from sqlalchemy.orm import Session, joinedload
from app.core.security import get_current_user
from app.models.product import Product
from app.db.session import get_db
from app.models.user import User

router = APIRouter(
    prefix="/helma-shop-api/v1/order",
    tags=["Order"],
)


# =====================
# CREATE ORDER
# =====================


@router.post(
    "",
    response_model=OrderOut,
)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # =====================
    # GET CUSTOMER PROFILE
    # =====================

    profile = (
        db.query(CustomerProfile)
        .filter(CustomerProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "profile",
                "message": "لطفاً ابتدا اطلاعات کاربری خود را تکمیل کنید",
            },
        )

    # =====================
    # CHECK RECEIVER INFO
    # =====================

    if not profile.first_name or not profile.last_name:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "profile",
                "message": "نام و نام خانوادگی گیرنده وارد نشده است",
            },
        )

    if not profile.address:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "address",
                "message": "آدرس گیرنده وارد نشده است",
            },
        )

    # =====================
    # CREATE ORDER
    # =====================

    order = Order(
        receiver_postal_code=profile.postal_code,
        receiver_first_name=profile.first_name,
        receiver_longitude=profile.longitude,
        receiver_last_name=profile.last_name,
        receiver_mobile=current_user.mobile,
        receiver_latitude=profile.latitude,
        receiver_address=profile.address,
        status=OrderStatus.PENDING,
        user_id=current_user.id,
        discount_amount=0,
        shipping_amount=0,
        payable_amount=0,
        total_amount=0,
    )

    db.add(order)
    db.flush()

    # =====================
    # CREATE ORDER ITEMS
    # =====================

    total_amount = 0

    for item_data in data.items:

        product = db.query(Product).filter(Product.id == item_data.product_id).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail={
                    "field": "product_id",
                    "message": "محصول مورد نظر یافت نشد",
                },
            )

        if item_data.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "field": "quantity",
                    "message": "تعداد محصول باید بیشتر از صفر باشد",
                },
            )

        unit_price = product.price
        total_price = unit_price * item_data.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            quantity=item_data.quantity,
            unit_price=unit_price,
            total_price=total_price,
        )

        db.add(order_item)

        total_amount += total_price

    # =====================
    # CALCULATE TOTALS
    # =====================

    discount_amount = 0
    shipping_amount = 0

    payable_amount = total_amount - discount_amount + shipping_amount

    order.total_amount = total_amount
    order.discount_amount = discount_amount
    order.shipping_amount = shipping_amount
    order.payable_amount = payable_amount

    db.commit()

    db.refresh(order)

    # Load items for response
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items),
        )
        .filter(Order.id == order.id)
        .first()
    )

    return order


# =====================
# GET MY ORDERS
# =====================


@router.get(
    "",
    response_model=list[OrderOut],
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    orders = (
        db.query(Order)
        .options(
            joinedload(Order.items),
        )
        .filter(
            Order.user_id == current_user.id,
        )
        .order_by(
            Order.id.desc(),
        )
        .all()
    )

    return orders


# =====================
# GET MY ORDER DETAILS
# =====================


@router.get(
    "/{order_id}",
    response_model=OrderOut,
)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .options(
            joinedload(Order.items),
        )
        .filter(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "field": "order",
                "message": "سفارش مورد نظر یافت نشد",
            },
        )

    return order
