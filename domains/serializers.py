from bdb import set_trace

from accounts.serializers import UserSerializer
from django.db.models import Count
from rest_framework import serializers

from .models import (Cart, Category, DomainLeads, Domains, Negotiation,
                     Notification, SponsoredHeadlines, Videos, AccessLogs)

from accounts.models import (UserProfile)

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = '__all__'


class DomainSerializer(serializers.ModelSerializer):
    videos = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    startup_breeders_switch = serializers.SerializerMethodField()
    trade_switch = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()

    def get_videos(self, obj):
        return VideoSerializer(obj.user_domains, many=True).data

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_startup_breeders_switch(self, obj):
        if obj.startup_breeders_switch is True:
            return "Yes"
        return "No"

    def get_trade_switch(self, obj):
        if obj.trade_switch is True:
            return "Yes"
        return "No"

    def get_status_label(self, obj):
        try:
            return obj.get_status_display()
        except:
            return ""

    class Meta:
        model = Domains
        fields = ('id', 'domain_name', 'domain_extension', 'business_status', 'buyer_price', 'seller_price', 'min_offer',
                  'visits', 'video_pitch_leads', 'startup_breeders_switch', 'startup_breeders', 'created_at', 'updated_at',
                  'user', 'videos', 'trade_switch', 'trade_option', 'status', 'status_label')


class DomainLeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainLeads
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    domain_leads_obj = serializers.SerializerMethodField()
    from_request_user = serializers.SerializerMethodField()
    to_request_user = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_domain_leads_obj(self, obj):
        return DomainLeadsSerializer(obj.domain_leads).data

    def get_from_request_user(self, obj):
        return UserSerializer(obj.from_request).data

    def get_to_request_user(self, obj):
        return UserSerializer(obj.to_request).data

    def get_category(self, obj):
        return CategorySerializer(obj.category).data

    class Meta:
        model = Notification
        fields = ('id', 'domain_leads', 'domain_leads_obj', 'to_request', 'to_request_user', 'from_request', 'from_request_user',
                  'category')


class SponsoredHeadlinesSerializer(serializers.ModelSerializer):
    domain_obj = serializers.SerializerMethodField()
    user_obj = serializers.SerializerMethodField()
    category_obj = serializers.SerializerMethodField()

    def get_domain_obj(self, obj):
        return DomainSerializer(obj.domain).data

    def get_user_obj(self, obj):
        return UserSerializer(obj.user).data

    def get_category_obj(self, obj):
        return CategorySerializer(obj.category).data

    class Meta:
        model = SponsoredHeadlines
        fields = ('id', 'category_obj', 'user_obj', 'domain_obj',
                  'advertisement_price', 'created_at', 'updated_at')


class CartCategorySerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('category')

    def get_category(self, obj):
        cart_details = obj.cartdetails_cart.all()
        category_info = []
        for cart_obj in cart_details:
            cart_dict = {"name": cart_obj.category.name,
                         "quantity": cart_obj.quantity,
                         "unit_price": cart_obj.unit_price,
                         "sub_total": cart_obj.sub_total}
            category_info.append(cart_dict)
        return category_info


class CartSerializer(CartCategorySerializer):
    status_label = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'total_amount', 'status', 'category',
                  'status_label', 'created_at', 'updated_at')

    def get_status_label(self, obj):
        try:
            return obj.get_status_display()
        except:
            return ""


class CartListSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'total_amount', 'status', 'items',
                  'status_label', 'created_at', 'updated_at')

    def get_status_label(self, obj):
        try:
            return obj.get_status_display()
        except:
            return ""

    def get_items(self, obj):
        cart_details = obj.cartdetails_cart.all()
        category_info = []
        for cart_obj in cart_details:
            cat_obj = {"name": cart_obj.category.name,
                       "quantity": cart_obj.quantity,
                       "unit_price": cart_obj.unit_price,
                       "sub_total": cart_obj.sub_total}
            cart_dict = {"domain_ids": cart_obj.domain_ids,
                         "category": cat_obj}
            category_info.append(cart_dict)
        return category_info


class NegotiationSerializer(serializers.ModelSerializer):
    status_label = serializers.SerializerMethodField()
    domain_id = serializers.SerializerMethodField()
    domain_name = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = ('id', 'amount', 'status', 'domain_leads_id', 'domain_id',
                  'domain_name', 'status_label', 'created_at', 'updated_at')

    def get_status_label(self, obj):
        try:
            return obj.get_status_display()
        except:
            return ""

    def get_domain_name(self, obj):
        try:
            return obj.domain_leads.domain_name
        except:
            return ""

    def get_domain_id(self, obj):
        try:
            return obj.domain_leads.domain_id
        except:
            return ""


class DomainLeadsSummarySerializer(serializers.ModelSerializer):
    last_bid_amount = serializers.SerializerMethodField()
    last_bid_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    total_inquiries = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = DomainLeads
        fields = ('domain_id', 'domain_name', 'total_inquiries', 'status', 'last_bid_amount',
                  'last_bid_date', 'user')

    def get_user(self, obj):
        try:
            user_profile, is_available = UserProfile.objects.get_or_create(obj.user)
            return { 'first_name': obj.user.first_name, 'last_name': obj.user.last_name, 'ip_address': user_profile.ip_address }
        except:
            return { 'first_name': obj.user.first_name, 'last_name': obj.user.last_name, 'ip_address': 'undefined' }
        #return { 'is_available': obj.user.first_name }

    def get_last_bid_amount(self, obj):
        try:
            if obj.notification_domain_leads.last():
                return obj.notification_domain_leads.last().amount
            return ""
        except:
            return ""

    def get_last_bid_date(self, obj):
        try:
            if obj.notification_domain_leads.last():
                return obj.notification_domain_leads.last().updated_at
            return ""
        except:
            return ""

    def get_total_inquiries(self, obj):
        try:
            return Domains.objects.filter(id=obj.domain_id).annotate(total_views=Count("domainleads_domain"))[0].total_views
        except:
            return 0

    def get_status(self, obj):
        try:
            return obj.domain.get_status_display()
        except:
            return ""



class AccessLogSerializer(serializers.ModelSerializer):
    log_line = serializers.JSONField()
    class Meta:
        model = AccessLogs
        fields = '__all__'