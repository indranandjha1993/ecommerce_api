def configure_relationships():
    """
    Configure relationships between models after they are all loaded.
    This function should be called after all models have been imported.
    """
    from sqlalchemy.orm import relationship
    from app.models.user import User
    from app.models.address import Address

    # Remove the relationships defined in the model classes
    # and define them here explicitly

    # User relationships
    User.addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    User.carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    User.orders = relationship("Order", back_populates="user")
    User.reviews = relationship("Review", back_populates="user")

    # Address relationships
    Address.user = relationship("User", back_populates="addresses")
    Address.shipping_orders = relationship(
        "Order",
        foreign_keys="[Order.shipping_address_id]",
        back_populates="shipping_address"
    )
    Address.billing_orders = relationship(
        "Order",
        foreign_keys="[Order.billing_address_id]",
        back_populates="billing_address"
    )
