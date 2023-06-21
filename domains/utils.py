import json
import os

from urllib.parse import urlencode, ParseResult
import boto3
import requests
from botocore.client import Config
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from accounts.models import UserProfile
from domains.models import Domains, Videos


def get_user_role(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        return True, user_profile.user_role
    except Exception as e:
        return False, ""

def get_user_role_approval(user):
    try:
        user_profile = UserProfile.objects.get(user)
        return True, user_profile.user_role
    except Exception as e:
        return False, ""

def videos_search_filter(request):
    search_query = Q()
    search_text = request.GET.get("search", "")
    if search_text:
        search_data = search_text.split(" ")
        for search in search_data:
            search_query |= Q(file_name__icontains=search) | Q(
                description__icontains=search)

    if request.GET.get("status"):
        if str(request.GET.get("status")) == '1':
            status = Videos.ACCEPTED
        elif str(request.GET.get("status")) == '2':
            status = Videos.DECLINE
        elif str(request.GET.get("status")) == '3':
            status = Videos.UNDECIDED
        elif str(request.GET.get("status")) == '4':
            status = Videos.DELETED
        if status:
            search_query = search_query & Q(
                status=status)
    return search_query


def domain_leads_search_filter(request):
    search_query = Q()
    search_text = request.GET.get("search", "")
    if search_text:
        search_data = search_text.split(" ")
        for search in search_data:
            search_query |= Q(domain_name__icontains=search) | Q(
                domain_extension__icontains=search) | Q(business_status__icontains=search)
    return search_query


def notification_search_filter(request):
    search_query = Q()
    search_text = request.GET.get("search", "")
    if search_text:
        search_data = search_text.split(" ")
        for search in search_data:
            search_query |= Q(domain_leads__domain_name__icontains=search) | Q(domain_leads__domain_extension__icontains=search) | Q(
                category__name__icontains=search) | Q(category__template__icontains=search)
    return search_query


def domains_search_filter(request):
    search_query = Q()
    search_text = request.GET.get("key_word", "")
    if search_text:
        search_data = search_text.split(" ")
        for search in search_data:
            search_query |= Q(domain_name__icontains=search) | Q(
                domain_extension__icontains=search)
    if request.user.id:
        search_query = search_query & Q(
            user_id=request.user.id)

    if request.GET.get("id"):
        search_query = search_query & Q(
            id=request.GET.get("id"))

    if request.GET.get("domain_name"):
        search_query = search_query & Q(
            domain_name__contains=request.GET.get("domain_name"))

    if request.GET.get("business_status"):
        new_query = Q()
        arr = json.loads(request.GET.get("business_status")).split(',')
        #for business_status in json.loads(request.GET.get("business_status")):
        for business_status in arr:
            new_query |= Q(business_status__contains=business_status)
        search_query = search_query & new_query

    if request.GET.get("trade_options"):
        new_query = Q()
        arr = json.loads(request.GET.get("trade_options")).split(',')
        for trade_options in arr:
        #for trade_options in json.loads(request.GET.get("trade_options")):
            new_query |= Q( trade_option__contains=trade_options)
        search_query = search_query & new_query

    if request.GET.get("min_price") and request.GET.get("max_price"):
        search_query = search_query & Q(
            seller_price__range=(request.GET.get("min_price"), request.GET.get("max_price")))

    if request.GET.get("min_char") and request.GET.get("max_char"):
        search_query = search_query & Q(
            domainlen__range=(request.GET.get("min_char"), request.GET.get("max_char")))

    if request.GET.get("startswith"):
        search_query = search_query & Q(
            domain_name__startswith=request.GET.get("startswith"))

    if request.GET.get("endswith"):
        search_query = search_query & Q(
            domain_name__endswith=request.GET.get("endswith"))
    if request.GET.get("extensions") and request.GET.get("extensions") != '[]':
        new_query = Q()
        arr = json.loads(request.GET.get("extensions")).split(',')
        for extension in arr:
            new_query |= Q( domain_extension__contains=extension)
        search_query = search_query & new_query
    new_query = Q(is_approved=2)
    search_query = search_query & new_query
    print ( search_query )
    return search_query


def page_limit_offset(request):
    page_no = request.GET.get("page")
    limit = request.GET.get("limit")
    if not request.GET.get("limit") or request.GET.get("limit") == "":
        limit = 9999999
    if not request.GET.get("page") or request.GET.get("page") == "":
        page_no = 1
    page_no = int(page_no)
    limit = int(limit)
    start_limit = ((page_no - 1) * limit)
    end_limit = page_no * limit
    return start_limit, end_limit


def add_domain(domain_name, user_id, startup_breeders_switch, trade_switch):
    if len(domain_name.split('.')) == 1:
        return Response(
            {'errors': 'There is no domain extension.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        domain_extension = f".{domain_name.split('.', 1)[1]}"
    if Domains.objects.filter(domain_name=domain_name).exists():
        return domain_name
    else:
        Domains.objects.create(
            domain_name=domain_name, domain_extension=domain_extension,
            user_id=user_id, startup_breeders_switch=startup_breeders_switch,
            trade_switch=trade_switch)
        api_url = os.getenv('API_URL')
        api_token = os.getenv('API_TOKEN')
        url = f"{api_url}/addDomain.php?domain={domain_name}" \
              f"&access_token={api_token}"
        response = requests.get(url)
        print(response.status_code)


def generate_aws_url(key) -> str:
    s3 = boto3.client('s3',
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                      config=Config('s3v4'),
                      region_name=os.getenv('AWS_DEFAULT_REGION'))
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": os.getenv('AWS_STORAGE_BUCKET_NAME'),
            "Key": key,
            'ResponseContentType': 'video/mp4'
        },
        ExpiresIn=3600
    )


def sponsored_headlines_search_filter(request):
    search_query = Q()
    search_text = request.GET.get("search", "")
    if search_text:
        search_data = search_text.split(" ")
        for search in search_data:
            search_query |= Q(category__name__icontains=search) | Q(
                domain__domain_name__icontains=search)

    if request.GET.get("id"):
        search_query = search_query & Q(
            id=request.GET.get("id"))

    if request.GET.get("user_id"):
        search_query = search_query & Q(
            user_id=request.GET.get("user_id"))

    if request.GET.get("domain_id"):
        search_query = search_query & Q(
            domain_id=request.GET.get("domain_id"))

    if request.GET.get("category_id"):
        search_query = search_query & Q(
            category_id=request.GET.get("category_id"))
    return search_query


def negotiation_search_filter(request):
    search_query = Q()
    if request.GET.get("id"):
        search_query = search_query & Q(
            id=request.GET.get("id"))

    if request.GET.get("user_id"):
        search_query = search_query & Q(
            user_id=request.GET.get("user_id"))

    if request.GET.get("domain_lead_id"):
        search_query = search_query & Q(
            domain_leads_id=request.GET.get("domain_lead_id"))

    if request.GET.get("domain_id"):
        search_query = search_query & Q(
            domain_leads__domain_id=request.GET.get("domain_id"))

    if request.GET.get("amount"):
        search_query = search_query & Q(
            amount=request.GET.get("amount"))

    if request.GET.get("status"):
        search_query = search_query & Q(
            status=request.GET.get("status"))
    return search_query


def delete_domain(instance):
    domain = instance.domain_name
    # raise error if domain name is not valid.
    querydict = {
        'access_token': os.getenv('API_TOKEN'),
        'domain': domain
    }
    qs = urlencode(querydict)
    url = ParseResult(
        scheme='http',
        netloc='api.testnames.link',
        path='delDomain.php',
        query=qs,
        params='',
        fragment=''
    )
    response = requests.get(url.geturl())
    return response
