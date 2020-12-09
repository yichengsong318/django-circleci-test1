
def calculate_sale_amount(product, discount_code, currency):
    """

    :param product:
    :param discount_code:
    :param currency:
    :return:
    """
    multiple = currency.multiple
    price = product.price

    if discount_code is None:
        return int(price * multiple)

    reduction = discount_code.reduction

    if discount_code.reduction_type == "amount":
        return max([
            0,
            int((price - reduction) * multiple)
        ])
    else:
        # It's a percentage
        return int((price - price * reduction / 100) * multiple)
