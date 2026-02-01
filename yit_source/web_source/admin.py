from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
# Register your models here.
from web_source.models import User
from web_source.models import Campus
from web_source.models import Dic
from web_source.models import Buildings
from web_source.models import Rooms
from web_source.models import Devices
from web_source.models import Vlan
from web_source.models import IPnet
from web_source.models import IPspecial
from web_source.models import Tasks
from web_source.models import Notes
from web_source.models import Bigthings
from web_source.models import Systerms
from web_source.models import RLinks
from web_source.models import DLinks
from web_source.models import VLinks
from web_source.models import TLinks
from web_source.models import GX
from web_source.models import FZ
from web_source.models import JF
from web_source.models import DK
from web_source.models import telephone, guanjing, lujing


'''
#A form for creating new users. Includes all the required fields, plus a repeated password.
class UserCreationForm(forms.ModelForm):
    #idcode = forms.CharField(label="idcode",widget=forms.TextInput)
    #username = forms.CharField(label="username",widget=forms.TextInput)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["idcode", "username", "password"]
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
#A form for updating users. Includes all the fields on the user, but replaces the password field with admin's disabled password hash display field.
class UserChangeForm(forms.ModelForm):
    #这样重定义修改的form 管理员就不能改密码了
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = User
        fields = ["idcode", "username", "phone", "password", "is_active", "is_superuser"]
'''

# 如果您的自定义用户模型扩展了django.contrib.auth.models.AbstractUser，
# #则可以使用Django现有的django.contrib.auth.admin.UserAdmin类。 
# 但是，如果您的用户模型扩展了AbstractBaseUser，则需要定义自定义的ModelAdmin类。
# 可以继承默认的django.contrib.auth.admin.UserAdmin; 
# 但是，您需要覆盖任何引用django.contrib.auth.models.AbstractUser上不在您的自定义用户类上的字段的定义。
class MyUserAdmin(UserAdmin):
    #重定义修改的form 
    #form = UserChangeForm
    #add_form = UserCreationForm
    model = User
    #设置 list_display 来控制哪些字段显示在管理的变更列表页面,如果你不设置 list_display，管理网站将显示一个单列，显示每个对象的 __str__() 表示。
    list_display = ('idcode','username','phone','is_superuser','is_staff','is_active','admin_level','date_joined','last_login')  # Contain only fields in your `custom-user-model`
    #使用 list_display_links 来控制 list_display 中的字段是否以及哪些字段应该被链接到对象的 “更改” 页面,也就是哪个字段上加跳转链接
    #list_display_links = ('username',)
    #哪些字段能直接在列表页编辑，同一字段不能同时列在 list_editable 和 list_display_links 中 —— 一个字段不能既是表单又是链接
    #list_editable = ('username',)
    list_filter = ('idcode',)  # Contain only fields in your `custom-user-model` intended for filtering. Do not include `groups`since you do not have it
    #这些字段应该是某种文本字段，如 CharField 或 TextField。你也可以对 ForeignKey 或 ManyToManyField 进行相关查询，并使用查找 API “follow” 符号：search_fields = ['foreign_key__related_fieldname']
    search_fields = ('idcode',)  # Contain only fields in your `custom-user-model` intended for searching
    #为搜索框指定一个描述性文本，显示在它的下面。
    #search_help_text
    ordering = ('idcode',)  # Contain only fields in your `custom-user-model` intended to ordering
    #默认情况下，在管理网站中显示一个 ManyToManyField 是 <select multiple>。但是，多选框在选择很多项目时，会很难用。在这个列表中添加一个 ManyToManyField，就可以改用一个不显眼的 JavaScript “过滤器” 界面，
    #在选项中进行搜索。未选择和选择的选项并排出现在两个框中。参见 filter_vertical 来使用垂直界面。
    filter_horizontal = ( 'groups' , 'user_permissions') # Leave it empty. You have neither `groups` or `user_permissions`
    # There are duplicate field(s) in 'fieldsets[4][1]'. 下面的UserAdmin.fieldsets + 意思是使用原来具有的属性，扩展出以下属性，所以和原有的重复就引发duplicate错误
    '''
    fieldsets = UserAdmin.fieldsets + (
            ('user_info', {'fields': ('idcode','username','phone',)}),
    )'''

    # 该属性覆盖记录字段为空（None、空字符串等）的默认显示值。默认值是 - （破折号）。
    #empty_value_display = '-empty-'
    #控制动作栏在页面的哪个位置出现。默认情况下，管理员更改列表在页面顶部显示动作
    #actions_on_top = True
    #actions_on_bottom = False

    # 要在同一行显示多个字段，将这些字段包在自己的元组中。在这个例子中，url 和 title 字段将显示在同一行，content 字段将显示在它们下面的一行：
    # 使用 fields 选项在 “添加” 和 “更改” 页面的表单中进行简单的布局修改，比如只显示可用字段的子集，修改它们的顺序，或者将它们分成几行。
    # fields = (('url', 'title'), 'content')

    #设置 fieldsets 来控制管理员 “添加” 和 “更改” 页面的布局
    fieldsets =(
            ('user_info', {'fields': ('idcode','username','phone','password')}),
            ('Permissions', {'fields': ('is_active','is_superuser','admin_level','is_staff','groups')}),
            ('Important_dates', {'fields': ('last_login','date_joined')}),
    )
    add_fieldsets = (
            ('user_info', {'fields': ('idcode','username','phone','password1','password2')}),#这里要和上面的form对应  两个password
    )
    #如果DateTimeField设置了auto_Now_add=True导致，即使设置了editable=True，也是默认不支持修改
    # when using fieldsets which contain read-only fields, those fields must be listed in readonly_fields for them to be displayed.
    readonly_fields = ['date_joined']
    #提供了一个快速而简单的方法来覆盖一些 Field 选项，以便在管理中使用。formfield_overrides 是一个字典，它将字段类映射成一个参数的字典，以便在构造时传递给字段。
    # 一个具体的例子。formfield_overrides 最常见的用法是为某一类型的字段添加一个自定义部件。所以，想象一下，我们写了一个 RichTextEditorWidget，我们想用于大文本字段，而不是默认的 <textarea>。    
    #formfield_overrides
    #from myapp.widgets import RichTextEditorWidget
    #formfield_overrides = {models.TextField: {'widget': RichTextEditorWidget},}
    #设置 list_max_show_all 来控制 “全部显示” 的管理员更改列表页面上可以出现多少个项目。只有当总结果数小于或等于此配置时，管理才会在更改列表中显示 “全部显示” 链接。默认情况下，这个配置为 200。
    list_max_show_all = 20
    #设置 list_per_page 来控制每个分页的管理变更列表页面上出现多少个项目。默认情况下，设置为 100。
    list_per_page = 10
    #当值为 True 时，select_related() 总是会被调用。当值设置为 False 时，Django 将查看 list_display，如果有 ForeignKey，则调用 select_related()。
    #如果你需要更精细的控制，可以使用元组（或列表）作为 list_select_related 的值。空元组将阻止 Django 调用 select_related。list_select_related = ('author', 'category')
    list_select_related = True
    #用于分页的分页器类。默认情况下，使用 django.core.paginator.Paginator。如果自定义的分页器类没有和 django.core.paginator.Paginator 一样的构造函数接口，你还需要为 ModelAdmin.get_paginator() 提供一个实现。
    #paginator
    #将 prepopulated_fields 设置为一个字典，将字段名称映射到它应该预先填充的字段：  html的placeholder?
    #prepopulated_fields  = {"slug": ("title",)}
    #默认情况下，在创建、编辑或删除对象后，应用的过滤器会被保存在列表视图中。您可以通过将此属性设置为 False 来清除过滤器。
    #preserve_filters
    #默认情况下，Django 的管理对于 ForeignKey 或设置了 choices 的字段使用选择框界面（<select>）。如果字段存在于 radio_fields 中，Django 将使用单选按钮接口代替.在 django.contrib.admin 模块中选择使用 HORIZONTAL 或 VERTICAL
    #radio_fields = {"group": admin.VERTICAL}
    #默认情况下，Django 的管理员对 ForeignKey 的字段使用选择框接口（<select>）。有时候，你不想显示所有相关的实例在下拉框。raw_id_fields 部件在字段旁边显示一个放大镜按钮，允许用户搜索和选择一个值
    #raw_id_fields
    #如果 save_as 为 True，则 “保存并添加另一个” 将被 “另存为新” 按钮所取代，该按钮将创建一个新的对象（具有新的 ID），而不是更新现有的对象。
    #save_as
    #当 save_as=True 时，保存新对象后默认重定向到该对象的变更视图。如果设置 save_as_continue=False，则重定向到变更列表视图。
    #save_as_continue
    #设置 save_on_top 来在你的管理更改表格的顶部添加保存按钮。
    #save_on_top
    #设置 show_full_result_count 来控制是否应该在过滤后的管理页面上显示全部对象的数量（例如： 99 results (103 total)）。如果这个选项被设置为 False，则会显示 99 results (Show all) 这样的文字。
    #show_full_result_count
    #这个值可以是一个布尔标志，也可以是一个可调用对象。如果 True （默认），对象的 get_absolute_url() 方法将被用来生成网址。
    #如果你的模型有一个 get_absolute_url() 方法，但你不想让 “在站点上查看” 按钮出现，你只需要将 view_on_site 设置为 False
    view_on_site = True

    #覆盖或扩展基本的管理模板    
    #每个管理页面顶部的文字，作为 <h1> （
    admin.AdminSite.site_header = "网络数据管理"
    admin.AdminSite.site_title = "网络数据管理"
    #每个管理页面顶部的 “查看网站” 链接的 URL。默认情况下，site_url 是 /。将其设置为 None 以删除该链接
    #admin.AdminSite.site_url
    admin.AdminSite.index_title= '管理'
    #index_template
    #布尔值，决定是否在大屏幕上显示导航侧栏。默认情况下，它被设置为 True。
    admin.AdminSite.enable_nav_sidebar = True
    #管理网站登录视图将使用的自定义模板的路径。
    #AdminSite.login_template  AdminSite.logout_template AdminSite.password_change_template  AdminSite.password_change_done_template


admin.site.register(User,MyUserAdmin)
# unregister the Group model from admin.
#admin.site.unregister(Group)

class CampusAdmin(admin.ModelAdmin):
    model = Campus
    list_display = ('idcode','name')
    fields = ['idcode','name']
    search_fields = ('name',)
admin.site.register(Campus,CampusAdmin)

class DicAdmin(admin.ModelAdmin):
    model = Dic
    list_display = ('type','key','value')
    fields = ['type','key','value']
    search_fields = ('type','key','value')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('-type',)
    list_display_links = ('key','value')
    #list_editable = ('type',)
admin.site.register(Dic, DicAdmin)
'''
class BuildingsInline(admin.TabularInline):
    model = Dic.objects_type.get_a_type('Buildings')
    '''
class BuildingsAdmin(admin.ModelAdmin):
    model = Buildings
    #inlines = [BuildingsInline]
    list_display = ('campus','name','date_update','date2_update','idcode','num_wireless','num_wired','elec','wifi','dhcp','ipv6','eduroam',)
    #哪些字段能直接在列表页编辑，同一字段不能同时列在 list_editable 和 list_display_links 中 —— 一个字段不能既是表单又是链接
    list_editable = ('date_update','date2_update','num_wireless','num_wired','elec','wifi','dhcp','ipv6','eduroam',)
    #fields = ['campus','name','idcode','points','center_point','num_wireless','num_wired','elec','wifi','dhcp','ipv6','eduroam','date_update','date2_update']
    search_fields = ('name','idcode')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('campus','idcode')
    list_display_links = ('name','idcode')
    autocomplete_fields = ['dic_buildings']
    #raw_id_fields = ('dic',)
admin.site.register(Buildings,BuildingsAdmin)
class RoomsAdmin(admin.ModelAdmin):
    model = Rooms
    #inlines = [BuildingsInline]
    list_display = ('name','building','floor','room_type','important','core','conver','vacant','dic_rooms',)
    list_editable = ('room_type','important','core','conver','vacant','dic_rooms',)
    fields = ['name','building','floor','room_type','important','core','conver','vacant','dic_rooms','remarks','remarks2']
    search_fields = ('name','building__name')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('building','floor')
    list_display_links = ('name',)
    autocomplete_fields = ['dic_rooms','building']
admin.site.register(Rooms,RoomsAdmin)
class DevicesAdmin(admin.ModelAdmin):
    model = Devices
    list_display = ('ip','name','version','设备间','vacant1','vacant2','cabinet','index','dic_devices','dic_devices_j')
    def 设备间(self, obj):
        #self是DevicesAdmin   obj是实例
        return obj.room.name+'|'+obj.room.building.name
    list_editable = ('name','version','vacant1','vacant2','cabinet','index','dic_devices','dic_devices_j')
    fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic_devices','dic_devices_j','remarks']
    search_fields = ('name','ip','room__name')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('room','ip')
    list_display_links = ('ip',)
    autocomplete_fields = ['room','dic_devices','dic_devices_j']#你必须在相关对象的 ModelAdmin 上定义 search_fields，才能完成搜索使用它，例如搜索room的同时还要能关联到building，就得在room里的search_fields定义building__name。
    def room_mark(self, obj):
        #self是DevicesAdmin   obj是实例
        return obj.room.name+'|'+obj.room.building.name
admin.site.register(Devices,DevicesAdmin)
class VlanAdmin(admin.ModelAdmin):
    model = Vlan
    list_display = ('name','remarks')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('name','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('name',)
    list_display_links = ('name',)
    #autocomplete_fields = ['room','dic']
admin.site.register(Vlan,VlanAdmin)
class IPnetAdmin(admin.ModelAdmin):
    model = IPnet
    list_display = ('network','netmask','netmask_int','vlan','building','supervlan_is','supervlan_parent','free','dic_ipvlanloc','dic_ipnetmask','remarks')
    fields = ['network','netmask','netmask_int','vlan','building','supervlan_is','supervlan_parent','free','dic_ipvlanloc','dic_ipnetmask','remarks']
    search_fields = ('remarks','network','netmask','netmask_int','free',)
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('network','vlan',)
    list_display_links = ('network',)
    autocomplete_fields = ['vlan','supervlan_parent','dic_ipvlanloc','dic_ipnetmask','building',]
admin.site.register(IPnet,IPnetAdmin)
class IPspecialAdmin(admin.ModelAdmin):
    model = IPspecial
    list_display = ('ip','ipnet','dic_ipspecial','remarks')
    fields = ['ip','ipnet','dic_ipspecial','remarks']
    search_fields = ('ip','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('ip',)
    list_display_links = ('ip',)
    autocomplete_fields = ['ipnet','dic_ipspecial',]
admin.site.register(IPspecial,IPspecialAdmin)
class TasksAdmin(admin.ModelAdmin):
    model = Tasks
    list_display = ('name','user','dic_tasks','date_start','date_end','detail','done','date_remain','always')
    fields = ['name','user','dic_tasks','date_start','date_end','detail','done','date_remain','always','remarks']
    search_fields = ('name','detail')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('done','date_start','name')
    list_display_links = ('name','detail',)
    autocomplete_fields = ['dic_tasks','user']
admin.site.register(Tasks,TasksAdmin)
class NotesAdmin(admin.ModelAdmin):
    model = Notes
    list_display = ('name','user','dic_notes','detail','remarks')
    fields = ['name','user','dic_notes','detail','remarks']
    search_fields = ('name','detail')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('dic_notes','user','name')
    list_display_links = ('name','detail',)
    autocomplete_fields = ['dic_notes','user']
admin.site.register(Notes,NotesAdmin)
class BigthingsAdmin(admin.ModelAdmin):
    model = Bigthings
    list_display = ('name','user','dic_bigthings','date_happen','charge','pic','specs','remarks')
    fields = ['name','user','dic_bigthings','date_happen','charge','pic','specs','remarks']
    search_fields = ('name','remarks','charge')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('date_happen','charge','name')
    list_display_links = ('name',)
    autocomplete_fields = ['dic_bigthings','user']
admin.site.register(Bigthings,BigthingsAdmin)
class SystermsAdmin(admin.ModelAdmin):
    model = Systerms
    list_display = ('name','dic_systerms','use','ip','ssl','wlj','date_gb','wk','os')
    fields = ['name','dic_systerms','use','wlj','ip','port','ssl','date_run','date_gb','wk','os','plus','remarks']
    search_fields = ('name','ip','plus')
    list_max_show_all = 20
    list_per_page = 30
    ordering = ('date_run','ip',)
    list_display_links = ('name','ip',)
    autocomplete_fields = ['dic_systerms',]
admin.site.register(Systerms,SystermsAdmin)
class RLinksAdmin(admin.ModelAdmin):
    model = RLinks
    list_display = ('from_room','current_room','to_room','vacant',)
    fields = ['from_room','current_room','to_room','vacant','remarks']
    search_fields = ('current_room',)
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('current_room',)
    list_display_links = ('current_room',)
    autocomplete_fields = ['from_room','current_room','to_room']
admin.site.register(RLinks,RLinksAdmin)
class DLinksAdmin(admin.ModelAdmin):
    model = DLinks
    list_display = ('current_device','index','from_device','to_device')
    fields = ['current_device','index','from_device','to_device','remarks']
    search_fields = ('current_device',)
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('current_device','index')
    list_display_links = ('current_device',)
    autocomplete_fields = ['current_device','from_device','to_device']
admin.site.register(DLinks,DLinksAdmin)
class VLinksAdmin(admin.ModelAdmin):
    model = VLinks
    list_display = ('vlan','building','remarks')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('vlan','building','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('building','vlan')
    list_display_links = ('vlan','building')
    autocomplete_fields = ['vlan','building']
admin.site.register(VLinks,VLinksAdmin)
class TLinksAdmin(admin.ModelAdmin):
    model = TLinks
    list_display = ('task','brief','detail')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('task','brief','detail')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('task',)
    list_display_links = ('task',)
    autocomplete_fields = ['task',]
admin.site.register(TLinks,TLinksAdmin)
class GXAdmin(admin.ModelAdmin):
    model = GX
    list_display = ('name','long','remarks')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('name','long','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('name',)
    list_display_links = ('name',)
admin.site.register(GX,GXAdmin)
class FZAdmin(admin.ModelAdmin):
    model = FZ
    list_display = ('name','num','remarks')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('name','num','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('name',)
    list_display_links = ('name',)
admin.site.register(FZ,FZAdmin)
class JFAdmin(admin.ModelAdmin):
    model = JF
    list_display = ('name','area','area2','ups','ups2','remarks')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('name','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('name',)
    list_display_links = ('name',)
admin.site.register(JF,JFAdmin)
class DKAdmin(admin.ModelAdmin):
    model = DK
    list_display = ('name','num','remarks')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('name','remarks')
    list_max_show_all = 20
    list_per_page = 10
    ordering = ('name',)
    list_display_links = ('name',)
admin.site.register(DK,DKAdmin)
class TELAdmin(admin.ModelAdmin):
    model = telephone
    list_display = ('num','location','tc','hb')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('num','location')
    list_max_show_all = 20
    list_per_page = 20
    ordering = ('num',)
    list_display_links = ('num',)
admin.site.register(telephone,TELAdmin)
class GJAdmin(admin.ModelAdmin):
    model = guanjing
    list_display = ('info','dic_guanjing','location1','location2','campus')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('info','campus')
    list_max_show_all = 20
    list_per_page = 20
    #ordering = ('num',)
    list_display_links = ('info',)
    autocomplete_fields = ['dic_guanjing']
admin.site.register(guanjing,GJAdmin)
class LujingAdmin(admin.ModelAdmin):
    model = lujing
    list_display = ('info','points','g','z')
    #fields = ['ip','name','version','room','vacant1','vacant2','cabinet','index','dic','remarks']
    search_fields = ('info','points')
    list_max_show_all = 20
    list_per_page = 20
    #ordering = ('num',)
    list_display_links = ('info',)
admin.site.register(lujing,LujingAdmin)
