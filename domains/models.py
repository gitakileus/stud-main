from accounts.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser

class Domains(models.Model):
    OPEN_FOR_SALE = 1
    NEGOTIATION = 2
    BROKER = 3
    SOLD = 4

    DOMAIN_STATUS = (
        (OPEN_FOR_SALE, 'Open For Sale'),
        (NEGOTIATION, 'Negotiation'),
        (BROKER, 'Broker'),
        (SOLD, 'Sold'),
    )

    NEW = 1
    APPROVED = 2
    DENIED = 3
    DOMAIN_APPROVED = (
        (NEW, 'New'),
        (APPROVED, 'Approved'),
        (DENIED, 'Denied'),
    )

    user = models.ForeignKey(User, related_name='user',
                             on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=50, blank=True)
    domain_extension = models.CharField(max_length=20, blank=True)
    business_status = models.CharField(max_length=30, blank=True)
    buyer_price = models.IntegerField(default=0, blank=True)
    seller_price = models.IntegerField(default=0, blank=True)
    min_offer = models.IntegerField(default=0, blank=True)
    visits = models.IntegerField(default=0, blank=True)
    video_pitch_leads = models.IntegerField(default=0, blank=True)
    startup_breeders_switch = models.BooleanField(
        default=False, null=True, blank=True)
    startup_breeders = models.CharField(max_length=20, blank=True)
    trade_switch = models.BooleanField(default=False, null=True, blank=True)
    trade_option = models.CharField(max_length=20, blank=True)
    status = models.SmallIntegerField(
        choices=DOMAIN_STATUS, default=OPEN_FOR_SALE)
    is_approved = models.SmallIntegerField(choices=DOMAIN_APPROVED, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.domain_name

    class Meta:
        db_table = 'domains'


class Videos(models.Model):
    ACCEPTED = 1
    DECLINE = 2
    UNDECIDED = 3
    DELETED = 4

    VIDEOS_STATUS = (
        (ACCEPTED, 'Accepted'),
        (DECLINE, 'Decline'),
        (UNDECIDED, 'Undecided'),
        (DELETED, 'Deleted')
    )
    user = models.ForeignKey(
        User, related_name='user_videos', on_delete=models.CASCADE)
    domain = models.ForeignKey(
        Domains, related_name='user_domains', on_delete=models.CASCADE, blank=True)
    file_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(null=True, blank=True)
    status = models.SmallIntegerField(choices=VIDEOS_STATUS, default=UNDECIDED)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'videos'


class DomainLeads(models.Model):
    user = models.ForeignKey(
        User, related_name='domainleads_user', on_delete=models.CASCADE)
    domain = models.ForeignKey(
        Domains, related_name='domainleads_domain', on_delete=models.CASCADE, blank=True)
    domain_name = models.CharField(max_length=50, blank=True)
    domain_extension = models.CharField(max_length=20, blank=True)
    business_status = models.CharField(max_length=30, blank=True)
    buyer_price = models.IntegerField(default=0, blank=True)
    seller_price = models.IntegerField(default=0, blank=True)
    min_offer = models.IntegerField(default=0, blank=True)
    visits = models.IntegerField(default=0, blank=True)
    video_pitch_leads = models.IntegerField(default=0, blank=True)
    startup_breeders = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    trade_option = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'domainleads'


class AccessLogs(models.Model):
    domain = models.CharField(max_length=255, blank=True)
    log_line = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'accesslog'


class Category(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    template = models.TextField(null=True, blank=True)
    advertisement_price = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'category'


class Notification(models.Model):
    domain_leads = models.ForeignKey(
        DomainLeads, related_name='notification_domain_leads', on_delete=models.CASCADE, blank=True)
    from_request = models.ForeignKey(
        User, related_name='notificaiton_from_request', on_delete=models.CASCADE)
    to_request = models.ForeignKey(
        User, related_name='notificaiton_to_request', on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, related_name='notificaiton_category', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'notification'


class SponsoredHeadlines(models.Model):
    user = models.ForeignKey(
        User, related_name='sponsored_user', on_delete=models.CASCADE)
    domain = models.ForeignKey(
        Domains, related_name='sponsored_domain', on_delete=models.CASCADE, blank=True)
    category = models.ForeignKey(
        Category, related_name='sponsored_category', on_delete=models.CASCADE)
    advertisement_price = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'sponsoredheadlines'


class Cart(models.Model):
    PENDING = 1
    COMPLETED = 2

    CART_STATUS = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed')
    )
    user = models.ForeignKey(
        User, related_name='cart_user', on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=0, null=True, blank=True)
    status = models.SmallIntegerField(choices=CART_STATUS, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'cart'


class CartDetails(models.Model):
    cart = models.ForeignKey(
        Cart, related_name='cartdetails_cart', on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, related_name='cartdetails_category', on_delete=models.CASCADE)
    domain_ids = models.JSONField(null=True, blank=True)
    quantity = models.IntegerField(default=0, blank=True)
    unit_price = models.IntegerField(default=0, blank=True)
    sub_total = models.IntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'cartdetails'


class Order(models.Model):
    BUY_NOW = 1
    CASH_ON_DELIVERY = 2

    PAYMENT_MODE_STATUS = (
        (BUY_NOW, 'Online'),
        (CASH_ON_DELIVERY, 'Cash On Delivery')
    )

    PENDING = 1
    PROCESSED = 2

    ORDER_STATUS = (
        (PENDING, 'Pending'),
        (PROCESSED, 'Processed')
    )

    user = models.ForeignKey(
        User, related_name='order_user', on_delete=models.CASCADE)
    total_amount = models.IntegerField(default=0, blank=True)
    payment_mode = models.SmallIntegerField(
        choices=PAYMENT_MODE_STATUS, default=CASH_ON_DELIVERY)
    order_status = models.SmallIntegerField(
        choices=ORDER_STATUS, default=PROCESSED)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'order'


class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order, related_name='orderdetails_order', on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, related_name='orderdetails_category', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, blank=True)
    unit_price = models.IntegerField(default=0, blank=True)
    sub_total = models.IntegerField(default=0, blank=True)
    total_amount = models.IntegerField(default=0, blank=True)
    domain_ids = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'orderdetails'


class Negotiation(models.Model):
    INITIAL_OFFER = 1
    COUNTER_OFFER = 2
    BUYER_OFFER = 3
    APPROVED = 4
    ASSIGNED_TO_BROKER = 5
    BIDDING_WAR = 6
    STARTUP_BREEDER_BUDGET = 7

    NEGOTIATION_STATUS = (
        (INITIAL_OFFER, 'Initial Offer'),
        (COUNTER_OFFER, 'Counter Offer'),
        (BUYER_OFFER, 'Buyer Offer'),
        (APPROVED, 'Approved'),
        (ASSIGNED_TO_BROKER, 'Assigned To Broker'),
        (BIDDING_WAR, 'Bidding War'),
        (STARTUP_BREEDER_BUDGET, 'Startup Breeder Budget')
    )
    domain_leads = models.ForeignKey(
        DomainLeads, related_name='negotiation_domain_leads', on_delete=models.CASCADE, blank=True)
    user = models.ForeignKey(
        User, related_name='negotiation_order_user', on_delete=models.CASCADE)
    amount = models.IntegerField(default=0, blank=True)
    status = models.SmallIntegerField(
        choices=NEGOTIATION_STATUS, default=INITIAL_OFFER)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'negotiation'

