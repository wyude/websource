from django.shortcuts import render, redirect, HttpResponse, reverse, get_object_or_404
import logging,time,string
from django.core import serializers
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404, HttpResponse,  HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.views.decorators import csrf
import re
import json
from IPy import IP
from django.db.models.functions import ExtractYear,Abs,Now

from web_source.models import *
from django.db import DatabaseError, transaction
from django.db.models import Avg, Max, Count, F, Q, Sum


def time_str():
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
'''
def mylog(name):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', filename=name+'_'+str(int(time.time()))+'.log',  filemode='w')
    logger = logging.getLogger()
    kzt = logging.StreamHandler()
    kzt.setLevel(logging.INFO)
    logger.addHandler(kzt)
    logging.info('{}'.format('日志初始化完成'+time_str()))
mylog('web_source')
logging.info('打开首页:{}-{}'.format('index',time_str()))
'''
# Create your views here.
def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]#这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')#这里获得代理ip
    return ip

# 子网掩码地址转长度
def netmask_to_bit_length(netmask):
    """
    >>> netmask_to_bit_length('255.255.255.0')
    24
    >>>
    """
    # 分割字符串格式的子网掩码为四段列表
    # 计算二进制字符串中 '1' 的个数
    # 转换各段子网掩码为二进制, 计算十进制
    return sum([bin(int(i)).count('1') for i in netmask.split('.')])

#gateway or any ip compute netname
def ip_2_netname(ip,mask):
    a = IP(ip).make_net(mask)
    return a.strNormal(0)


#if the ip in the network
def is_ip_in(ip,netname,mask):
    if netname and mask:
        return ip in IP(netname+'/'+mask)
    else:
        return False

def is_ip_overlapped(netname,mask,netname2,mask2):
    return IP(netname+'/'+mask).overlaps(netname2+'/'+mask2)

#check ip formate
def is_ip(ipAddr):
  compile_ip=re.compile('^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
  if compile_ip.match(ipAddr):
    return True 
  else:  
    return False
  
@login_required
def logout(request):
    request.encoding = 'utf-8'
    logout(request)
    return redirect('web_source:index')

@require_http_methods(['POST',])
def login(request):
    request.encoding = 'utf-8'
    '''
    args = request.POST
    try:
        idcode = args['idcode']
        pwd = args['pwd']
    except:
        return redirect('web_source:index')
    user = authenticate(request, username=idcode, password=pwd)
    if user:
        login(request, user)
        # request.session.set_expiry(None)#设置session过期时间，None表示使用系统默认的过期时间.0代表关闭浏览器session失效
        # return render(request, 'index3.html', {'user': user})
        return redirect('web_source:index')
    else:
        return redirect('web_source:login')
    '''
    return redirect('admin:login')
    
@login_required  
@require_http_methods(['GET',])
def index(request):
    request.encoding = 'utf-8'
    user = request.user
    print(user,user.username,user.password,user.is_authenticated,user.is_staff,user.is_superuser)
    data = {}
    rooms = Rooms.objects.all()
    if rooms:
        num_rooms = rooms.count()
        data['num_rooms'] = num_rooms
        data['num_rooms_j'] = rooms.filter(room_type="A").count()
        data['num_rooms_g'] = rooms.filter(room_type="B").count()
        data['num_rooms_hj'] = rooms.filter(conver=True).count()
        data['num_rooms_zd'] = rooms.filter(important=True).count()
        data['num_rooms_hx'] = rooms.filter(core=True).count()
    buildings = Buildings.objects.all()
    if buildings:
        data['num_wired'] = buildings.aggregate(num=Sum('num_wired'))['num']
        data['num_wireless'] = buildings.aggregate(num=Sum('num_wireless'))['num']
    devices = Devices.objects.all()
    if devices:
        data['num_devices_jhj'] = devices.filter(dic_devices__value='交换机').count()
        data['num_devices_am'] = devices.filter(dic_devices__value='AM').count()
        data['num_devices_ac'] = devices.filter(dic_devices__value='AC').count()
        data['num_devices_ly'] = devices.filter(dic_devices__value='路由').count()
        data['num_devices_hx'] = devices.filter(dic_devices__value='核心').count()
        data['num_devices_fhq'] = devices.filter(dic_devices__value='防火墙').count()
    jf = JF.objects.all().order_by('date_create')
    if jf:
        jf = jf.first()
        data['area_d'] = jf.area
        data['area_x'] = jf.area2
        data['ups_d'] = jf.ups
        data['ups_x'] = jf.ups2
    fz = FZ.objects.all()
    data['fz'] = fz
    gx = GX.objects.all()
    if gx:
        gx = gx.aggregate(num=Sum('long'))
        data['num_long'] = gx['num']
    dk = DK.objects.all()
    data['dk'] = dk
    return render(request, '../view/index.html', {'data': data,})

@login_required 
@require_http_methods(['GET','POST'])
def searchip(request):
    request.encoding = 'utf-8'
    data = {}
    if request.method == 'POST':
        args = request.POST
        ip = args.get('ipv4')
        if not is_ip(ip):
            data['error'] = '提交的IP被篡改！'
        else:
            check = args.get('check')
            ip_special = IPspecial.objects.filter(ip = ip)
            res = []
            for v in ip_special:
                if v.ipnet and v.ipnet.vlan:
                    vlinks = v.ipnet.vlan.vlan_vlinks.all()
                    vb = []
                    for b in vlinks:
                        vb.append(b.building.name)
                    res.append({'ip':v.ip,'dic':v.dic_ipspecial.value,'remarks':v.remarks,'network':v.ipnet.network,'netmask':v.ipnet.netmask,'netmask_int':v.ipnet.netmask_int,'vlan':v.ipnet.vlan.name,'buildings':vb})
                else:
                    res.append({'ip':v.ip,'dic':v.dic_ipspecial.value}) 
            print(res)
            ip_special = res
            ip0 = ip.split('.')[0]
            ips = IPnet.objects.filter(network__startswith = ip0)
            ip_n = []
            for v in ips:
                if is_ip_in(ip,v.network,v.netmask):
                    vlinks = v.vlan.vlan_vlinks.all()
                    vb = [v.building.name,]
                    for b in vlinks:
                        vb.append(b.building.name)
                    ip_n.append({'vlan':v.vlan.name, 'network':v.network,'netmask':v.netmask,'netmask_int':v.netmask_int,'free':v.free,'remarks':v.remarks,'buildings':vb})
            if 'true' in check:
                pass
            print(ip_n)
            data['ip_special'] = ip_special
            data['ip_n'] = ip_n
        data['ipv4'] = ip
        data['check'] = check
        return JsonResponse({"data":data })
    return render(request, '../view/searchip.html', {'data': data,})

@login_required 
@require_http_methods(['GET','POST'])
def map(request):
    request.encoding = 'utf-8'
    data = {}
    if request.method == 'POST':
        args = request.POST.get('id',None)
        if args:
            binfo = Buildings.objects.values('name','idcode','wifi','dhcp','eduroam','elec','campus__name','date_update','date2_update','num_wireless','num_wired').get(idcode=args)
            rinfo = Rooms.objects.values('id','name','floor','room_type').filter(building__idcode=args).order_by('floor')
            rinfo = list(rinfo)
            dinfo = Devices.objects.values('id','name','version','room__id','room__building__idcode',).filter(room__building__idcode=args)
            dinfo = list(dinfo)
            ipinfo = IPnet.objects.values('remarks','network','netmask','netmask_int').filter(building__idcode=args)
            ipinfo = list(ipinfo)
            print(ipinfo)
            for d in dinfo:
                i = 0
                for r in rinfo:
                    if r['id'] == d['room__id']:
                        if 'dinfo' not in rinfo[i]:
                            rinfo[i]['dinfo'] = []
                        rinfo[i]['dinfo'].append(d)
                    i = i + 1
            binfo['rinfo'] = rinfo
            binfo['ipinfo'] = ipinfo
            binfo['rinfo_num'] = len(rinfo)
            binfo['dinfo_num'] = len(dinfo)
            #print(binfo)
        elif request.POST.get('zhongdian',None):
            args = request.POST.get('zhongdian',None)
            rinfo = Rooms.objects.values('id','building__idcode','building__center_point').filter(important=True)
            binfo = list(rinfo)
        return JsonResponse({'data': binfo})
    else:
        data = Buildings.objects.filter(points__isnull=False).only('name','idcode','points','center_point','wifi','dhcp','eduroam','elec')
        data2 = data.annotate(
            year1=ExtractYear('date_update'),
            year2=ExtractYear('date2_update'),
            gt_10_1=Abs(ExtractYear('date_update')-ExtractYear(Now())),
            gt_10_2=Abs(ExtractYear('date2_update')-ExtractYear(Now()))
            ).values('name','idcode','points','center_point','wifi','dhcp','eduroam','elec','year1','year2','gt_10_1','gt_10_2')
        #data2 = serializers.serialize("json", data2)
        #print(data2)
        data2 = json.dumps(list(data2))
    return render(request, '../view/map.html', {'data': data,'data2':data2})


@login_required 
@require_http_methods(['GET'])
def cacCenter(request):
    request.encoding = 'utf-8'
    data = Buildings.objects.filter(points__isnull=False).only('name','idcode','points',).all()
    for pp in data:
        px = 0
        py = 0
        ps = pp.points.split(',')
        #print(ps)
        n = len(ps)/2
        for i, value in enumerate(ps):
            if i%2 == 0:
                px = px + int(value)
            else:
                py = py + int(value)
        px = int(px / n)
        py = int(py / n)
        Buildings.objects.filter(idcode=pp.idcode).update(center_point=str(px)+','+str(py)) 
    data2 = data.values('name','idcode','points')
    #data2 = serializers.serialize("json", data2)
    data2 = json.dumps(list(data2))
    return render(request, '../view/map.html', {'data': data,'data2':data2})

@login_required 
@require_http_methods(['GET'])
def map_online(request):
    request.encoding = 'utf-8'
    points = guanjing.objects.values('info','campus__name','location1','location2')
    print(points)
    return render(request, '../view/map_online.html', {'points':points})

@login_required 
def wells(request):
    request.encoding = 'utf-8'
    points = guanjing.objects.all().values('location1', 'location2','info','campus__name', 'dic_guanjing__key', 'img' ,'remarks')
    points = json.dumps(list(points))
    #points = serializers.serialize('json',points)
    print(points)
    return JsonResponse(points, safe=False)

@login_required 
def paths(request):
    request.encoding = 'utf-8'
    res = lujing.objects.all().values('info', 'points' ,'g','z','zt','remarks')
    res = json.dumps(list(res))
    #res = serializers.serialize('json',res)
    print(res)
    return JsonResponse(res, safe=False)

@login_required 
def update_status(request):
    request.encoding = 'utf-8'
    
    return JsonResponse(None, safe=False)