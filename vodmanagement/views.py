from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.template import RequestContext
from mysite.settings import STATIC_URL
from .forms import VodForm
from django.contrib import messages
from filer.models import Image
from .models import *
from django.core import serializers
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q
from django.core.cache import cache
def gallery(request):
    # if not request.user.is_staff or not request.user.is_superuser:
    #     raise Http404
    form = VodForm(request.POST or None, request.FILES or None)
    print('get form ok!')
    if  form.is_valid():
        image_file = form.cleaned_data['image']
        # Image.save()
        # instance = form.save()
        # instance = request.user
        # instance.save()
        # message success
        messages.success(request, "Successfully Created")
        print('form valid')
        # return render(request, "vodmanagement/gallery.html")
    # context = {
    #     "form": form,
    # }
    else:
        print('form is invalid')
    return render(request, "vodmanagement/gallery.html")
    # if request.method == 'POST' and request.FILES:
        # myfile=request.FILES['name_file']
        # print('file:'+myfile.name)
        # form=DocumentForm(request.POST,request.FILES)
        # print('form OK!')
        # if form.is_valid():
        #     print('Save OK!')
        #     form.save()
        #     return HttpResponseRedirect('homepage')

    # return render(request,'vodmanagement/gallery.html')
def categorys():
    categorys = VideoCategory.objects.filter(type='common')
    return categorys


def homepage(request):
    user = request.user
    content = None
    # if request.user.is_authenticated():
        # content = {
        #     # 'active_menu': 'homepage',
        #     'user': user.username,
        # }
        # print('user:'+user.username)

    # categorys = VideoCategory.objects.filter(type='common')
    content = {
            'categorys': categorys(),
            'user': user.username,
        }
    return render(request,'vodmanagement/base.html',content)


# Create your views here.
def login(request):
    state = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print('username:'+username)
        print('password:'+password)
        user = auth.authenticate(username=username, password=password)
        print(user)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('vod:homepage'))
        else:
            state = 'not_exist_or_password_error'
    content = {
        'active_menu': 'homepage',
        'state': state,
        'user': None
    }
    print('retry')
    return render(request,'vodmanagement/login.html',content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))

# divide data into few pages
def listing(request,slug=None):
    if slug is None:
        title = "All Videos"
        video_list = Vod.objects.all()#filter(category__name=slug)
    else:
        title = slug
        video_list = Vod.objects.filter(category__name=slug)

    #search word
    query = request.GET.get('search_word')
    if query:
        video_list = video_list.filter(
            Q(title__icontains=query)|
            Q(category__name__icontains=query)|
            Q(description__icontains=query)|
            Q(short_description__icontains=query)
            ).distinct()

    video_page = Paginator(video_list,4)
    # print('total pages:'+str(video_page.count))
    page=request.GET.get('page')
    try:
        videos = video_page.page(page)
    except PageNotAnInteger:
        videos = video_page.page(1)
    except EmptyPage:
        videos = video_page.page(video_page.num_pages)
    
    # categorys = VideoCategory.objects.filter(type='common')
    content={
        'videos':videos,
        'categorys': categorys(),
        'title': title,
    }
    return render(request,'vodmanagement/list.html',content)

def listinglink(request):
    link_list = Link.objects.all()
    link_page = Paginator(link_list,6)
    # print('total pages:'+str(video_page.count))
    page=request.GET.get('page')
    try:
        links = link_page.page(page)
    except PageNotAnInteger:
        links = link_page.page(1)
    except EmptyPage:
        links = link_page.page(link_page.num_pages)
    content={
        'links':links,
    }
    return render(request,'vodmanagement/listlink.html',content)

def vod_detail(request,slug=None):
    print(slug)
    instance = get_object_or_404(Vod, slug=slug)
    instance.view_count += 1
    # cache.set('key',instance)
    instance.save()
    print(instance.view_count )
    context = {
        "video":instance,
        'categorys': categorys(),
    }
    return render(request,'vodmanagement/detail.html',context)

# @login_required
def ajax_get_data(request):
       json_data = serializers.serialize("json", Vod.objects.all())
       return HttpResponse(json_data,content_type="application/json")