import pandas as pd, re
from django.db import IntegrityError
from django.db.models import Count, Q
from django.db.models.functions import Length
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from accounts.serializers import CustomerSerializer, UserSerializer
from domains.custom_exception import CustomException
from domains.filters import LogFilter
from accounts.models import Customer
from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist

import json

from domains.models import (AccessLogs, Cart, CartDetails, Category, DomainLeads, Domains,
                            Negotiation, Notification, Order, OrderDetails,
                            SponsoredHeadlines, Videos)
from domains.serializers import (AccessLogSerializer, CartListSerializer, CartSerializer,
                                 CategorySerializer, DomainLeadsSerializer,
                                 DomainLeadsSummarySerializer,
                                 DomainSerializer, NegotiationSerializer,
                                 NotificationSerializer,
                                 SponsoredHeadlinesSerializer, VideoSerializer)
from domains.utils import (add_domain, delete_domain, domain_leads_search_filter,
                           domains_search_filter, generate_aws_url,
                           get_user_role, negotiation_search_filter,
                           notification_search_filter, page_limit_offset,
                           sponsored_headlines_search_filter,
                           videos_search_filter, get_user_role_approval)
from django_filters import rest_framework as filters
from django.http import HttpResponse

class SearchDomainAPI(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        search_results = []
        search_query = domains_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        result = Domains.objects.annotate(domainlen=Length('domain_name')).filter(
            search_query).order_by(order_by)[start:end]
        serializer = DomainSerializer(result, many=True)
        search_results.extend(serializer.data)

        return Response(data=search_results, status=status.HTTP_200_OK)


class DomainViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, ]

    @staticmethod
    def list(request):
        search_query = domains_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        domains = Domains.objects.filter(
            search_query).order_by(order_by)[start:end]
        serializer = DomainSerializer(domains, many=True)
        return Response({'domains': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        user_id = request.user.id
        domain_list = request.data['domain_list'].split(',')
        domain_file = request.FILES.get('file')
        exist_domains = []

        if domain_file:
            domain_file_extension = domain_file.name.split('.')[1]
            if domain_file_extension not in ['csv', 'xls', 'txt']:
                return Response(
                    {'message': 'Please try again with these file formats(xls, txt, csv).'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if domain_file_extension == 'csv' or domain_file_extension == 'txt':
                data = pd.read_csv(domain_file, header=None)
            else:
                data = pd.read_excel(domain_file)
            self.validate_domain_names(data.values())
            for domain in data.values:
                domain_name = domain[0]
                try:
                    startup_breeders_switch = domain[1]
                    trade_switch = domain[2]
                except:
                    startup_breeders_switch = False
                    trade_switch = False
                add_domain(domain_name, user_id,
                            startup_breeders_switch, trade_switch)
        if domain_list:
            self.validate_domain_names(domain_list)
            for domain_name in domain_list:
                exist_domain_name = add_domain(
                    domain_name, user_id, False, False)
                exist_domains.append(exist_domain_name)

        return Response({'existing_domains': exist_domains}, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def validate_domain_names(domains):
        pattern = "^((?:([a-z0-9]\.|[a-z0-9][a-z0-9\-]{0,61}[a-z0-9])\.)+)([a-z0-9]{2,63}|(?:[a-z0-9][a-z0-9\-]{0,61}[a-z0-9]))\.?$"
        invalid_domains = [d.strip() for d in domains if not re.fullmatch(pattern, d)]
        if invalid_domains:
            raise CustomException(detail="Invalid Domains : {}".format(",".join(invalid_domains)))
        return True


    @staticmethod
    def update(request, pk=None):
        domain_array = request.data['domain_ids']
        data = []
        for id in domain_array:
            try:
                domain = Domains.objects.get(pk=id)
                try:
                    domain.is_approved = request.data['is_approved']
                except:
                    pass
                try:
                    domain.domain_name = request.data['domain_name']
                except:
                    pass
                try:
                    domain.seller_price = request.data['seller_price']
                except:
                    print ( 'exception' )
                    pass
                try:
                    domain.min_offer = request.data['min_offer']
                except:
                    pass
                try:
                    domain.business_status = request.data['business_status']
                except:
                    pass
                try:
                    domain.trade_option = request.data['trade_option']
                except:
                    pass
                try:
                    domain.startup_breeders = request.data['startup_breeders']
                except:
                    pass
                try:
                    if request.data.get('startup_breeders_switch').lower() == "yes":
                        domain.startup_breeders_switch = True
                    else:
                        domain.startup_breeders_switch = False
                except:
                    pass
                try:
                    if request.data.get('trade_switch').lower() == "yes":
                        domain.trade_switch = True
                    else:
                        domain.trade_switch = False
                except:
                    pass
                domain.save()
                data=DomainSerializer(domain).data
            except IntegrityError:
                return Response({'error': 'This domain already exists.'}, id=id, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'The domains are updated successfully'}, status=status.HTTP_200_OK)
    @staticmethod
    def destroy(request, pk=None):
        domain_array = json.loads(request.body)
        for id in domain_array['domain_ids']:
            print (id)
            try:
                domain = Domains.objects.get(pk=id)
            except Domains.DoesNotExist:
                domain = None
            domain.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @staticmethod
    def retrieve(request, pk=None):
        try:
            domain = Domains.objects.get(pk=pk)
        except Domains.DoesNotExist:
            domain = None
        #print (domain)
        #domain = Domains.objects.get(pk=pk)
        serializer = DomainSerializer(domain)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class VideoUploadAPI(APIView):
    permissions = [permissions.IsAuthenticated]

    def post(self, request):
        file_name = request.data['file_name']
        domain_id = request.data['domain_id']
        description = request.data.get('description', '')

        if Domains.objects.filter(pk=domain_id).exists():
            domain = Domains.objects.get(pk=domain_id)
            Videos.objects.create(
                domain=domain, file_name=file_name, user=request.user, description=description)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetVideoAPI(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request, pk):
        if Videos.objects.filter(pk=pk):
            video = Videos.objects.get(pk=pk)
            video_url = generate_aws_url(video.file_name)

            return Response(data=video_url, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class MyStable(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        domains = Domains.objects.filter(user_id=1).values_list('id')
        domain_ids = [domain[0] for domain in domains]

        domain_leads_count = DomainLeads.objects.filter(
            domain__in=domain_ids).count()
        videos_count = Videos.objects.filter(domain__in=domain_ids).count()

        result = {
            "domain_leads": domain_leads_count,
            "video_pitch_leads": videos_count,
            "recently_viewed_domains": 0,
            "market_count": 0
        }
        return Response(result, status=status.HTTP_200_OK)


class VideoView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        search_query = videos_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        user_status, user_role = get_user_role(request)
        if user_status is True and user_role.lower() == 'seller':
            domains = Domains.objects.filter(
                user=request.user).values_list('id')
            domain_ids = [domain[0] for domain in domains]
            search_query = search_query & Q(domain__in=domain_ids)
        else:
            search_query = search_query & Q(user=request.user)
        videos_list = Videos.objects.filter(
            search_query).order_by(order_by)[start:end]
        result = VideoSerializer(videos_list, many=True).data
        return Response(result, status=status.HTTP_200_OK)


class DomainLeadsView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        search_query = domain_leads_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        user_status, user_role = get_user_role(request)
        if user_status is True and user_role.lower() == 'seller':
            print ( user_role )
            domains = Domains.objects.filter(
                user=request.user).values_list('id')
            domain_ids = [domain[0] for domain in domains]
            search_query = search_query & Q(domain__in=domain_ids)
        else:
            search_query = search_query & Q(user=request.user)

        leads_list = DomainLeads.objects.filter(
            search_query).order_by(order_by)[start:end]
        result = DomainLeadsSerializer(leads_list, many=True).data
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        domain_id = request.data['domain_id']

        if Domains.objects.filter(pk=domain_id).exists():
            domain = Domains.objects.get(pk=domain_id)
            obj = DomainLeads.objects.create(
                domain=domain, user=request.user,
                domain_name=domain.domain_name,
                domain_extension=domain.domain_extension,
                business_status=domain.business_status,
                buyer_price=domain.buyer_price,
                seller_price=domain.seller_price,
                min_offer=domain.min_offer,
                visits=domain.visits,
                video_pitch_leads=domain.video_pitch_leads,
                startup_breeders=domain.startup_breeders,
                trade_option=domain.trade_option)
            return Response({"domain_lead_id": obj.id}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NotificationView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        search_query = notification_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        search_query = search_query & Q(
            Q(from_request=request.user) | Q(to_request=request.user))
        notifications = Notification.objects.filter(
            search_query).order_by(order_by)[start:end]

        result = NotificationSerializer(notifications, many=True).data
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        domain_lead_id = request.data['domain_lead_id']
        if DomainLeads.objects.filter(pk=domain_lead_id).exists():
            try:
                domain_leads = DomainLeads.objects.filter(
                    pk=domain_lead_id).first()
                category_obj = Category.objects.filter(
                    name__contains=request.data['category']).first()

                Notification.objects.create(
                    domain_leads=domain_leads,
                    from_request=request.user,
                    to_request=domain_leads.user,
                    category=category_obj)
                return Response(status=status.HTTP_200_OK)
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SponsoredHeadlinesView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        search_query = sponsored_headlines_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        leads_list = SponsoredHeadlines.objects.select_related("user", "domain", 'category').filter(
            search_query).order_by(order_by)[start:end]
        result = SponsoredHeadlinesSerializer(leads_list, many=True).data
        return Response({'message': 'Sponsored'}, status=status.HTTP_200_OK)

    def post(self, request):
        for sponsored in request.data["data"]:
            category = Category.objects.get(
                name__icontains=sponsored['category'])
            for sponso in sponsored["domain_ids"]:
                domain_id = sponso

                if Domains.objects.filter(pk=domain_id).exists():
                    domain = Domains.objects.get(pk=domain_id)
                    SponsoredHeadlines.objects.create(
                        domain=domain,
                        user=request.user,
                        category=category,
                        advertisement_price=category.advertisement_price)
        return Response(status=status.HTTP_200_OK)


class OrderView(APIView):
    permissions = [permissions.IsAuthenticated]

    def post(self, request):
        cart_objs = CartDetails.objects.filter(
            cart_id=request.data.get("cart_id"))

        order_obj = Order.objects.create(
            user=request.user
        )
        total_amount = 0
        for cart_obj in cart_objs:
            total_amount += cart_obj.sub_total
            OrderDetails.objects.create(
                order=order_obj,
                category=cart_obj.category,
                quantity=cart_obj.quantity,
                unit_price=cart_obj.category.advertisement_price,
                sub_total=cart_obj.sub_total,
                total_amount=cart_obj.sub_total,
                domain_ids=cart_obj.domain_ids
            )
            for car_obj in cart_obj.domain_ids:
                domain_id = car_obj

                if Domains.objects.filter(pk=domain_id).exists():
                    domain = Domains.objects.get(pk=domain_id)
                    SponsoredHeadlines.objects.create(
                        domain=domain,
                        user=request.user,
                        category=cart_obj.category,
                        advertisement_price=cart_obj.category.advertisement_price)
        order_obj.total_amount = total_amount
        order_obj.save()
        return Response(status=status.HTTP_200_OK)


class SponsoredCartView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        cart_objects = Cart.objects.filter(
            user=request.user).order_by(order_by)[start:end]
        result = CartListSerializer(cart_objects, many=True).data
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        if request.data.get("cart_id"):
            cart_obj = Cart.objects.get(id=request.data.get("cart_id"))
        else:
            cart_obj = Cart.objects.create(
                user=request.user, status=Cart.PENDING)

        for cartobj in request.data['items']:
            category = Category.objects.get(
                name__icontains=cartobj['category'])
            quantity = len(cartobj['domain_ids'])
            sub_total = quantity * category.advertisement_price

            CartDetails.objects.create(
                cart=cart_obj,
                category=category,
                domain_ids=cartobj['domain_ids'],
                quantity=quantity,
                unit_price=category.advertisement_price,
                sub_total=sub_total
            )
        result = CartSerializer(cart_obj).data
        return Response(result, status=status.HTTP_200_OK)


class CategoryView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        categories = Category.objects.all().order_by(order_by)[start:end]
        result = CategorySerializer(categories, many=True).data
        return Response(result, status=status.HTTP_200_OK)


class NegotiationView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        search_query = negotiation_search_filter(request)
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'

        negotiation_list = Negotiation.objects.select_related("domain_leads").filter(
            search_query).order_by(order_by)[start:end]

        result = NegotiationSerializer(negotiation_list, many=True).data
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        domain_leads = DomainLeads.objects.get(
            id=request.data.get("domain_lead_id"))
            
        Negotiation.objects.create(
            domain_leads=domain_leads,
            user=request.user,
            amount=request.data.get("amount"),
            status=request.data.get("status"))
        return Response(status=status.HTTP_200_OK)


class DomainLeadSummaryView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = page_limit_offset(request)
        if request.GET.get('order_by'):
            order_by = request.GET.get('order_by')
        else:
            order_by = '-created_at'
        domain_leads = DomainLeads.objects.prefetch_related("negotiation_domain_leads").select_related("domain").filter(
            domain__user=request.user).distinct("domain_id", "domain_name").order_by("domain_id", "domain_name", order_by)[start:end]
        result = DomainLeadsSummarySerializer(domain_leads, many=True).data
        return Response(result, status=status.HTTP_200_OK)


class AccessLogView(ListAPIView):
    permissions = [permissions.IsAuthenticated]
    serializer_class = AccessLogSerializer
    queryset = AccessLogs.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = LogFilter
   

class ApprovalView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def get(self, request):
        start, end = page_limit_offset(request)
        users = User.objects.all()[start:end]
        user_total_count = User.objects.all().count()
        domain_total_count = Domains.objects.all().count()
        domain_new_total_count = Domains.objects.filter(is_approved=1).count()
        domain_approved_total_count = Domains.objects.filter(is_approved=2).count()
        domain_denied_total_count = Domains.objects.filter(is_approved=3).count()
        total_count = ({ 'user': user_total_count, 'domain': domain_total_count, 'domain_new': domain_new_total_count, 'domain_approved': domain_approved_total_count, 'domain_denied': domain_denied_total_count })
        result = []
        for user in users:
            domain_new_count = Domains.objects.filter(
                user=user, is_approved=1).count()
            domain_approved_count = Domains.objects.filter(
                user=user, is_approved=2).count()
            domain_denied_count = Domains.objects.filter(
                user=user, is_approved=3).count()
            result.append({'user_id': user.id, 'user_name': user.first_name + ' ' + user.last_name, 'new': domain_new_count, 'approved': domain_approved_count, 'denied': domain_denied_count})
        
        return Response({'commonInfo': total_count, 'userInfo': result}, status=status.HTTP_200_OK)

class ApprovalDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    def get(self, request, pk):
        if User.objects.filter(pk=pk):
            user = User.objects.get(pk=pk)
            domains = Domains.objects.filter(user=user)
            domain_count = Domains.objects.filter(
                user=user).count()
            domain_approved_count = Domains.objects.filter(
                user=user, is_approved=2).count()
            domain_denied_count = Domains.objects.filter(
                user=user, is_approved=3).count()
            user_status, user_role = get_user_role_approval(user)
            user_ = {
                'id': user.id,
                'name': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_role': user_role
            }
            user_info = ({'user': user_, 'domain_total': domain_count, 'domain_approved': domain_approved_count, 'domain_denied': domain_denied_count})
            result = []
            for domain in domains:
                domain_ = {
                    'id': domain.id,
                    'name': domain.domain_name,
                    'is_approved': domain.is_approved
                }
                result.append(domain_)
            return Response({'userInfo': user_info, 'domainInfo': result}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class UsersView(APIView):
    permissions = [permissions.IsAuthenticated]
    def get(self, request):
        start, end = page_limit_offset(request)
        users = User.objects.all().select_related('customer')
        result = []        
        for user in users:
            user_ = {
                'id': user.id,
                'name': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
            try: 
                user_['role'] = user.customer.role
            except:
                user_['role'] = 0
            result.append(user_)
        
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get("id")
        role = request.data.get("role")
        user = User.objects.get(id=user_id)
        try:
            customer = Customer.objects.get(user=user)
            customer.role = role
            customer.save()
        except:
            Customer.objects.create(
                user=user,
                role=role
            )
        
        user = User.objects.get(id=user_id)
        result = {
            'id': user.id,
            'name': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.customer.role
        }
        return Response(result, status=status.HTTP_200_OK)