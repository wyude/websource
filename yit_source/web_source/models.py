#encode = 'utf-8'

from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
from datetime import datetime
from django.utils import timezone
# Create your models here.

#total = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
class UserManager(BaseUserManager):
    def create_user(self,idcode,username,password):
        if not idcode:
            raise ValueError("Users must have an idcode")
        if not username:
            raise ValueError("Users must have an username")
        if not password:
            raise ValueError("Users must have an password")
        user = self.model(idcode=idcode,username=username,password=password)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self,idcode,username,password):
        user = self.create_user(idcode=idcode,username=username,password=password)
        user.is_superuser = True
        user.isstaff = True
        user.save()
        return user
#扩展 AbstractUser类
#如果你对django自带的User model刚到满意, 又希望额外的field的话, 你可以扩展AbstractUser类:
#扩展 AbstractBaseUser类
#AbstractBaseUser中只含有3个field: password, last_login和is_active. 如果你对django user model默认的first_name, last_name不满意, 或者只想保留默认的密码储存方式, 则可以选择这一方式.
#使用OneToOneField
#如果你想建立一个第三方模块发布在PyPi上, 这一模块需要根据用户储存每个用户的额外信息
class User(AbstractUser):
    GENDER_TYPE = (
        ("1", "男"),
        ("0", "女")
    )
    idcode = models.CharField(max_length=10, verbose_name="工号", unique=True,primary_key=True)
    username = models.CharField(max_length=20,  null=True, blank=True, verbose_name="姓名")
    gender = models.CharField(max_length=2, choices=GENDER_TYPE, verbose_name="性别", null=True, blank=True)
    phone = models.CharField(max_length=11, null=True, blank=True, unique=True, verbose_name="手机号码")
    admin_level = models.IntegerField(default=0, verbose_name="权限等级")
    ##如果DateTimeField设置了auto_Now_add=True导致，即使设置了editable=True，也是默认不支持修改
    # when using fieldsets which contain read-only fields, those fields must be listed in readonly_fields for them to be displayed.
    date_joined = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    #USERNAME_FIELD = "username"表示该model类中用哪个字段表示用户名。这个字段指定行为是必要操作，用于Django验证用户名密码以及后台登录等操作。
    USERNAME_FIELD = 'idcode'
    class Meta:
        #db_table定义在数据库创建该表时的表名为什么，不指定默认为django_user
        db_table = "users"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.idcode
    def get_full_name(self):
        return self.username
    def get_short_name(self):
        return self.username
    #在通过 createsuperuser 管理命令创建用户时，将提示用户输入的字段名称列表。用户将被提示为每个字段提供一个值。它必须包括 blank 为 False 或未定义的任何字段，并可能包括你希望在交互式创建用户时提示的其他字段。REQUIRED_FIELDS 在 Django 的其他部分没有效果，比如在管理中创建用户。
    REQUIRED_FIELDS = ['username']
    objects = UserManager()


class Campus(models.Model):
    idcode = models.CharField(max_length=10, verbose_name="校区编码", unique=True, primary_key=True)
    name = models.CharField(max_length=10, verbose_name="校区名称", unique=True)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    class Meta:
        db_table = "Campus"
        verbose_name = "校区表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name
    
class DicManager(models.Manager):
    def get_a_type(self,type):
        return super().get_queryset().filter(type=type)
    
class Dic(models.Model):
    key = models.CharField(max_length=10, verbose_name="键")
    value = models.CharField(max_length=10, verbose_name="值")
    type = models.CharField(max_length=10, verbose_name="分类")
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)  
    class Meta:
        db_table = "Dic"
        verbose_name = "字典表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.value
    objects = models.Manager()  # The default manager.
    objects_type = DicManager()


    

class Buildings(models.Model):
    idcode = models.CharField(max_length=10, verbose_name="楼宇编码", unique=True, primary_key=True)
    name = models.CharField(max_length=10, verbose_name="楼宇名称", unique=True)
    campus = models.ForeignKey(Campus, verbose_name="校区", related_name="buildings_campus", on_delete=models.PROTECT)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    points = models.CharField(max_length=200, verbose_name="位置点坐标",blank=True,null=True)
    center_point = models.CharField(max_length=50,verbose_name="位置中点",blank=True,null=True)
    elec = models.BooleanField(default=False, verbose_name="独立供电")
    wifi = models.BooleanField(default=False, verbose_name="wifi覆盖")
    dhcp = models.BooleanField(default=False, verbose_name="启用DHCP")
    ipv6 = models.BooleanField(default=False, verbose_name="启用IPV6")
    eduroam = models.BooleanField(default=False, verbose_name="启用eduroam")
    date_update = models.DateField(blank=True, null=True, verbose_name="有线网络改造时间")
    date2_update = models.DateField(blank=True, null=True, verbose_name="无线网络改造时间")
    dic_buildings = models.ForeignKey(Dic, blank=True ,null=True, verbose_name="介质类型", related_name="dic_buildings", on_delete=models.PROTECT)
    num_wireless = models.IntegerField(verbose_name="无线点位数",blank=True,null=True)
    num_wired = models.IntegerField(verbose_name="有线点位数",blank=True,null=True)
    class Meta:
        db_table = "Buildings"
        verbose_name = "楼宇表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name
    

class Rooms(models.Model):
    ROOM_TYPE = (
        ('A','弱电间'),
        ('B','弱电机柜')
    )
    name = models.CharField(max_length=50, verbose_name="房间名称")
    building = models.ForeignKey(Buildings, verbose_name="所在楼宇", related_name="buildings_rooms", on_delete=models.PROTECT)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    floor = models.IntegerField(default=1, verbose_name="楼层")
    room_type = models.CharField(max_length=2, choices=ROOM_TYPE, verbose_name="弱电间/机柜", default="A")
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    remarks2 = models.TextField(max_length=100,verbose_name="其他备注",blank=True,null=True)
    important = models.BooleanField(default=False, verbose_name="重点节点")
    core = models.BooleanField(default=False, verbose_name="核心节点")
    conver = models.BooleanField(default=False, verbose_name="汇聚节点")
    vacant = models.IntegerField(default=0, verbose_name="下连剩余光纤口数量")
    dic_rooms = models.ForeignKey(Dic, blank=True ,null=True, verbose_name="类型", related_name="dic_rooms", on_delete=models.PROTECT)
    class Meta:
        db_table = "Rooms"
        verbose_name = "设备间表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name
    def get_room_type_text(self):
        return dict(self.ROOM_TYPE).get(self.room_type, '')

class RLinks(models.Model):
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    current_room = models.ForeignKey(Rooms, verbose_name="当前房间", related_name="current_rooms", on_delete=models.PROTECT)
    from_room = models.ForeignKey(Rooms, blank=True, null=True, verbose_name="上连房间", related_name="from_rooms", on_delete=models.PROTECT)
    to_room = models.ForeignKey(Rooms, blank=True, null=True, verbose_name="下连房间", related_name="to_rooms", on_delete=models.PROTECT)
    vacant = models.IntegerField(default=0, verbose_name="剩余光纤口数量")
    class Meta:
        db_table = "RLinks"
        verbose_name = "设备间连通表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.current_room.name
    

class Devices(models.Model):
    ip = models.CharField(max_length=200,verbose_name="管理IP",blank=True, null=True, unique=True)
    name = models.CharField(max_length=100, verbose_name="品牌")
    version = models.CharField(max_length=100, verbose_name="型号")
    room = models.ForeignKey(Rooms, verbose_name="所在房间", related_name="rooms_devices", on_delete=models.PROTECT)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    vacant1 = models.IntegerField(default=0, verbose_name="剩余网口数量")
    vacant2 = models.IntegerField(default=0, verbose_name="剩余光口数量")
    cabinet = models.IntegerField(default=1, verbose_name="所在机柜")
    index = models.IntegerField(default=0, verbose_name="所在位置xU")
    dic_devices = models.ForeignKey(Dic, blank=True ,null=True, verbose_name="设备类型", related_name="dic_devices", on_delete=models.PROTECT)
    dic_devices_j = models.ForeignKey(Dic, blank=True ,null=True, verbose_name="介质类型", related_name="dic_devices2", on_delete=models.PROTECT)
    class Meta:
        db_table = "Devices"
        verbose_name = "设备表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.ip    
    

class DLinks(models.Model):
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    current_device = models.ForeignKey(Devices, verbose_name="当前设备", related_name="current_devices", on_delete=models.PROTECT)
    index = models.IntegerField(default=0, verbose_name="端口号")
    from_device = models.ForeignKey(Devices, blank=True, null=True, verbose_name="上连设备", related_name="from_devices", on_delete=models.PROTECT)
    to_device = models.ForeignKey(Devices, blank=True, null=True, verbose_name="下连设备", related_name="to_devices", on_delete=models.PROTECT)
    class Meta:
        db_table = "DLinks"
        verbose_name = "设备连通表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.current_device.name
    


class Vlan(models.Model):
    name = models.IntegerField(default=0,verbose_name="vlan",unique=True)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "Vlan"
        verbose_name = "Vlan表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return 'vlan'+str(self.name)
    

class IPnet(models.Model):
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    network = models.CharField(max_length=200,verbose_name="network",blank=True,null=True)
    netmask = models.CharField(max_length=200,verbose_name="netmask",blank=True,null=True)
    netmask_int = models.IntegerField(verbose_name="netmask_int",blank=True,null=True)
    vlan = models.ForeignKey(Vlan, null=False, blank=False, verbose_name="所属Vlan", related_name="vlan_ipnet",on_delete=models.PROTECT)
    supervlan_parent = models.ForeignKey(Vlan, null=True, blank=True, verbose_name="所属supervlan", related_name="vlan_ipnet_supervlan",on_delete=models.PROTECT)
    free = models.BooleanField(default=False, null=True, blank=True, verbose_name="免认证")
    supervlan_is = models.BooleanField(default=False, null=True, blank=True, verbose_name="supervlan")
    dic_ipvlanloc = models.ForeignKey(Dic, null=True, blank=True, verbose_name="所属核心", related_name="dic_ipvlanloc",on_delete=models.PROTECT)
    dic_ipnetmask = models.ForeignKey(Dic, null=True, blank=True, verbose_name="分类描述", related_name="dic_ipnetmask",on_delete=models.PROTECT)
    building = models.ForeignKey(Buildings, null=True, blank=True, verbose_name="楼宇", related_name="buildings_ipnet",on_delete=models.PROTECT)
    class Meta:
        db_table = "IPnet"
        verbose_name = "IPnetmask表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.network    
    

class VLinks(models.Model):
    vlan = models.ForeignKey(Vlan, null=True, blank=True, verbose_name="Vlan", related_name="vlan_vlinks",on_delete=models.PROTECT)
    building = models.ForeignKey(Buildings, null=True, blank=True, verbose_name="楼宇", related_name="buildings_vlinks",on_delete=models.PROTECT)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "VLinks"
        verbose_name = "VlanBuilding关联表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return 'vlan'+str(self.vlan.name)
    

class IPspecial(models.Model):
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    ip = models.CharField(max_length=200,verbose_name="IP")
    ipnet = models.ForeignKey(IPnet, null=True, blank=True, verbose_name="所在IP名", related_name="ipnet_ipspecial",on_delete=models.PROTECT)
    dic_ipspecial = models.ForeignKey(Dic, blank=True ,null=True, verbose_name="固定、免认证", related_name="dic_ipspecial", on_delete=models.PROTECT)
    class Meta:
        db_table = "IPspecial"
        verbose_name = "特殊IP表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.ip   
    

class Tasks(models.Model):
    name = models.CharField(max_length=200, verbose_name="任务名称")
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    user = models.ForeignKey(User, verbose_name="任务负责人", related_name="user_tasks", blank=True, null=True, on_delete=models.PROTECT)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    date_start = models.DateField(blank=True, verbose_name="预计开始日期",null=True)
    date_end = models.DateField(blank=True, verbose_name="预计完成日期",null=True)
    detail = models.TextField(verbose_name="任务描述")
    done = models.BooleanField(default=False, verbose_name="是否完成",help_text="结了尾款才是完成")
    date_remain = models.DateField(blank=True,null=True, verbose_name="预计支付尾款日期")
    always = models.BooleanField(default=False, verbose_name="是否每年例行")
    dic_tasks = models.ForeignKey(Dic, verbose_name="任务所在年度", related_name="dic_tasks", on_delete=models.PROTECT)
    class Meta:
        db_table = "Tasks"
        verbose_name = "工作任务表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name   
    

class TLinks(models.Model):
    task = models.ForeignKey(Tasks, null=True, blank=True, verbose_name="任务名称", related_name="tasks_tlinks",on_delete=models.PROTECT)
    brief = models.TextField(verbose_name="简单描述")
    detail = models.TextField(verbose_name="任务描述",blank=True, null=True)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "TLinks"
        verbose_name = "task的其他追加信息表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.task.name
    


class Notes(models.Model):
    name = models.CharField(max_length=200, verbose_name="日志名称")
    remarks = models.TextField(verbose_name="备注", blank=True, null=True)
    user = models.ForeignKey(User, verbose_name="撰写人", related_name="user_notes", blank=True, null=True, on_delete=models.PROTECT)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    detail = models.TextField(verbose_name="任务描述", blank=True, null=True)
    dic_notes = models.ForeignKey(Dic, verbose_name="分类", related_name="dic_notes", on_delete=models.PROTECT)
    class Meta:
        db_table = "Notes"
        verbose_name = "工作日志表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name   
    

class Bigthings(models.Model):
    name = models.CharField(max_length=200, verbose_name="事件名称")
    remarks = models.TextField(verbose_name="备注", blank=True, null=True)
    user = models.ForeignKey(User, verbose_name="录入人", related_name="user_bigthings", blank=True, null=True, on_delete=models.PROTECT)
    charge = models.CharField(max_length=20,verbose_name="当时单位负责人")
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    date_happen = models.DateField(verbose_name="发生日期")
    dic_bigthings = models.ForeignKey(Dic, verbose_name="分类", related_name="dic_bigthings",blank=True, null=True, on_delete=models.PROTECT)
    pic = models.ImageField(upload_to='Bigthings',blank=True, null=True,verbose_name="事件图片")
    specs = models.FileField(upload_to='Bigthings',blank=True, null=True,verbose_name="事件附件")
    class Meta:
        db_table = "Bigthings"
        verbose_name = "大事件表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name   
    

class Systerms(models.Model):
    USE_TYPE = (
        ("1", "在用"),
        ("0", "已报废"),
        ("2", "测试"),
        ("3", "测试过")
    )
    name = models.CharField(max_length=200, verbose_name="系统名称")
    remarks = models.TextField(verbose_name="备注", blank=True, null=True)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    date_run = models.DateField(verbose_name="上线日期", blank=True, null=True)
    date_gb = models.DateField(verbose_name="过保日期", blank=True, null=True)
    dic_systerms = models.ForeignKey(Dic, verbose_name="分类", related_name="dic_systerms",blank=True, null=True, on_delete=models.PROTECT)
    ip = models.CharField(max_length=200,verbose_name="地址", blank=True, null=True)
    port = models.CharField(max_length=10,verbose_name="远程端口", blank=True, null=True)
    ssl = models.BooleanField(default=False, verbose_name="使用SSL证书")
    wk = models.BooleanField(default=False, verbose_name="续保有尾款")
    os = models.CharField(max_length=100,verbose_name="操作系统", blank=True, null=True)
    plus = models.TextField(verbose_name="插件名称及版本", blank=True, null=True)
    use = models.CharField(max_length=2, choices=USE_TYPE, verbose_name="使用情况", default="1")
    wlj = models.BooleanField(default=False, verbose_name="物理服务器")
    class Meta:
        db_table = "Systerms"
        verbose_name = "管理系统表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name   
    

class GX(models.Model):
    name = models.CharField(verbose_name="段落名",unique=True,max_length=100)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    long = models.FloatField(verbose_name="长度",blank=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "GX"
        verbose_name = "光纤表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name    
    
class FZ(models.Model):
    name = models.CharField(verbose_name="负载名",unique=True,max_length=100)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    num = models.IntegerField(verbose_name="数量",blank=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "FZ"
        verbose_name = "负载表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name        
    
class JF(models.Model):
    name = models.CharField(verbose_name="机房信息",unique=True,max_length=100)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    area = models.FloatField(verbose_name="面积",blank=True, null=True)
    area2 = models.FloatField(verbose_name="面积2",blank=True, null=True)
    ups = models.FloatField(verbose_name="UPS时间东",blank=True, null=True)
    ups2 = models.FloatField(verbose_name="UPS时间西",blank=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "JF"
        verbose_name = "机房信息表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name   
    
class DK(models.Model):
    name = models.CharField(verbose_name="线路名",unique=True,max_length=100)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    num = models.FloatField(verbose_name="带宽",blank=True, null=True)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "DK"
        verbose_name = "带宽表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name      
class telephone(models.Model):
    num = models.CharField(verbose_name="号码",unique=True,blank=False,null=False,max_length=7)
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    location = models.CharField(verbose_name="位置",blank=False,null=False,max_length=100)
    tc = models.CharField(verbose_name="套餐",blank=False,null=False,max_length=20)
    hb = models.CharField(verbose_name="合并付费组",blank=False,null=False,max_length=20)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    class Meta:
        db_table = "TEL"
        verbose_name = "电话表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.num  

class guanjing(models.Model):
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    location1 = models.CharField(verbose_name="经度",blank=False,null=False,max_length=100)
    location2 = models.CharField(verbose_name="纬度",blank=False,null=False,max_length=100)
    campus = models.ForeignKey(Campus, verbose_name="校区", related_name="guanjing_campus", on_delete=models.PROTECT)
    dic_guanjing = models.ForeignKey(Dic, verbose_name="类型", related_name="guanjing_dic", on_delete=models.PROTECT,null=True)
    info = models.CharField(verbose_name="位置描述",blank=False,null=False,max_length=600)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    img = models.ImageField(verbose_name="水印图片", upload_to='guanjing/',default=[{}])
    class Meta:
        db_table = "GUANJING"
        verbose_name = "弱电管井表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.info  

class lujing(models.Model):
    date_create = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    points = models.TextField(verbose_name="途经点",blank=False,null=False)
    info = models.CharField(verbose_name="位置描述（哪到哪）",blank=False,null=False,max_length=200)
    remarks = models.TextField(verbose_name="备注",blank=True,null=True)
    g = models.IntegerField(verbose_name='根数',blank=False,null=False,default=1)
    z = models.IntegerField(verbose_name='总芯数',blank=False,null=False,default=0)
    zt = models.JSONField(verbose_name='芯状态',null=True)
    class Meta:
        db_table = "LUJING"
        verbose_name = "光缆路径表"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.info  