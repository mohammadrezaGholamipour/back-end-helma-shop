from app.schemas.order import OrderCreate, OrderOut,OrderItemOut
from app.models.customer_profile import CustomerProfile
from fastapi import APIRouter, Depends, HTTPException
from app.models.order import Order, OrderStatus
from sqlalchemy.orm import Session, joinedload
from app.core.security import get_current_user
from app.models.order_item import OrderItem
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
                "message": "نام و نام خانوادگی خود را وارد کنید",
            },
        )

    if not profile.address:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "address",
                "message": "لطفاً آدرس خود را وارد کنید",
            },
        )

    # =====================
    # CHECK ORDER ITEMS
    # =====================

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail={
                "field": "items",
                "message": "سبد خرید خالی است",
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

        # Order starts as pending
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

        # ---------------------
        # Validate quantity
        # ---------------------

        if item_data.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "field": "quantity",
                    "message": "تعداد محصول باید بیشتر از صفر باشد",
                },
            )

        # ---------------------
        # Get product
        # ---------------------

        product = (
            db.query(Product)
            .filter(Product.id == item_data.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail={
                    "field": "product_id",
                    "message": "محصول مورد نظر یافت نشد",
                },
            )

        # ---------------------
        # Get variant
        # ---------------------

        variant = (
            db.query(ProductVariant)
            .filter(
                ProductVariant.id == item_data.variant_id,
                ProductVariant.product_id == product.id,
            )
            .first()
        )

        if not variant:
            raise HTTPException(
                status_code=404,
                detail={
                    "field": "variant_id",
                    "message": "تنوع محصول مورد نظر یافت نشد",
                },
            )

        # ---------------------
        # Get price from database
        # ---------------------

        unit_price = variant.price

        if unit_price is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "field": "price",
                    "message": "قیمت این محصول مشخص نشده است",
                },
            )

        # ---------------------
        # Calculate item total
        # ---------------------

        total_price = unit_price * item_data.quantity

        # ---------------------
        # Create order item
        # ---------------------

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,

            # Important: save variant too
            variant_id=variant.id,

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

    payable_amount = (
        total_amount
        - discount_amount
        + shipping_amount
    )

    order.total_amount = total_amount
    order.discount_amount = discount_amount
    order.shipping_amount = shipping_amount
    order.payable_amount = payable_amount

    # =====================
    # COMMIT
    # =====================

    db.commit()

    db.refresh(order)

    # =====================
    # LOAD ORDER ITEMS
    # =====================

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


@router.delete("/{order_id}", status_code=204)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(status_code=404, detail="سفارش یافت نشد")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="فقط سفارش‌های در انتظار قابل حذف هستند",
        )

    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    db.delete(order)
    db.commit()