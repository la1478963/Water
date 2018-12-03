from django.conf import settings
from utlis.log_class import Logger
from rbac import models



def init_permission(user,request):
    logger = Logger(loglevel=1, logger="fox").getlog()
    """
    初始化权限信息，获取权限信息并放置到session中。
    :param user: Rbac
    :param request:
    :return:
    """
    permission_list =user.filter(pteamper__permissions__id__isnull=False).values(
                                        'pteamper__name',
                                        'pteamper__permissions__id',
                                        'pteamper__permissions__name',              # 用户列表
                                        'pteamper__permissions__url',
                                        'pteamper__permissions__code',
                                        'pteamper__permissions__menu_gp_id',         # 组内菜单ID，Null表示是菜单
                                        'pteamper__permissions__group_id',            # 权限的组ID
                                        'pteamper__permissions__group__menu_id',     # 权限的组的菜单ID
                                        'pteamper__permissions__group__menu__name', # 权限的组的菜单名称
                                        ).distinct()
    # 菜单相关（以后再匹配）,inclusion_tag
    menu_permission_list = []
    auth_permission_list = []
    request.session[settings.USER]=user.first().username
    request.session[settings.USERID]=user.first().id
    for item in permission_list:
        auth_tpl = {
            'id': item['pteamper__permissions__id'],
            'title': item['pteamper__permissions__name'],
            'url': item['pteamper__permissions__url'],
            'menu_gp_id': item['pteamper__permissions__menu_gp_id'],
            'menu_id': item['pteamper__permissions__group__menu_id'],
            'menu_title': item['pteamper__permissions__group__menu__name'],
        }
        #用于权限使用
        auth_permission_list.append(auth_tpl)
        if '实例' in item['pteamper__permissions__name'] or 'BacketName' in item['pteamper__permissions__name']\
                or '授权用户' in item['pteamper__permissions__name'] or '生产者' in item['pteamper__permissions__name']\
                or '消费者' in item['pteamper__permissions__name'] or 'Topic' in item['pteamper__permissions__name']:
            if user.first().username != 'boss':
                continue
        menu_tpl = {
            'id': item['pteamper__permissions__id'],
            'title': item['pteamper__permissions__name'],
            'url': item['pteamper__permissions__url'],
            'menu_gp_id': item['pteamper__permissions__menu_gp_id'],
            'menu_id': item['pteamper__permissions__group__menu_id'],
            'menu_title': item['pteamper__permissions__group__menu__name'],
        }
        #用于菜单使用(删除了很多内容)
        menu_permission_list.append(menu_tpl)
    request.session[settings.PERMISSION_MENU_KEY] = menu_permission_list
    request.session[settings.PERMISSION_AUTH_KEY] = auth_permission_list



    permission_dict={'app':[],'host':[],}
    pteam_obj=user.filter().values('pteams')
    #角色
    request.session[settings.PTEAM_OBJ] = pteam_obj.first()['pteams']
    app_id=models.App.objects.filter(pteamrole__in=user.first().pteams.all()).values_list('id','hosts')
    # host_id=models.App.objects.filter(pteamrole=orm_pteam).values('hosts')
    for num in app_id:
        permission_dict['app'].append(num[0])
        permission_dict['host'].append(num[1])
    request.session[settings.PERMISSION_HOST] = permission_dict

    # 权限相关，中间件
    """
    {
        1:{
            codes: [list,add,edit,del],
            urls: [  /userinfo/,  /userinfo/add/,  /userinfo/... ]
        },
        2:{
            codes: [list,add,edit,del],
            urls: [  /userinfo/,  /userinfo/add/,  /userinfo/... ]
        }
        3:{
            codes: [list,add,edit,del],
            urls: [  /userinfo/,  /userinfo/add/,  /userinfo/... ]
        }
    }
    """
    result = {}
    for item in  permission_list:
        try:
            group_id = item['pteamper__permissions__group_id']
            code = item['pteamper__permissions__code']
            url = item['pteamper__permissions__url']
            if group_id in result:
                result[group_id]['codes'].append(code)
                result[group_id]['urls'].append(url)
            else:
                result[group_id] = {
                    'codes':[code,],
                    'urls':[url,]
                }
        except KeyError as e:
            logger.error('auth,init_permission')
            logger.error(type(e))
            logger.error(e)
    request.session[settings.PERMISSION_URL_DICT_KEY] = result




########### restful 使用
def rest_init_permission(user,request):
    permission_list = user.filter(pteamper__permissions__id__isnull=False).values(
        'pteamper__name',
        'pteamper__permissions__id',
        'pteamper__permissions__name',  # 用户列表
        'pteamper__permissions__url',
        'pteamper__permissions__code',
        'pteamper__permissions__menu_gp_id',  # 组内菜单ID，Null表示是菜单
        'pteamper__permissions__group_id',  # 权限的组ID
        'pteamper__permissions__group__menu_id',  # 权限的组的菜单ID
        'pteamper__permissions__group__menu__name',  # 权限的组的菜单名称
    ).distinct()

    return permission_list




def rest_init_menu(user,request):
    menu_permission_list = []

    ret_dic={}
    permission_list=rest_init_permission(user, request)

    for item in permission_list:
        # 用于不显示一些特殊的内容，显得很乱
        if '实例' in item['pteamper__permissions__name'] or 'BacketName' in item['pteamper__permissions__name'] \
                or '授权用户' in item['pteamper__permissions__name'] or '生产者' in item['pteamper__permissions__name'] \
                or '消费者' in item['pteamper__permissions__name'] or 'Topic' in item['pteamper__permissions__name']:
            if user.first().username != 'boss':
                continue

        if item['pteamper__permissions__menu_gp_id']:
            #排除增删改
            # print('111111111',item['pteamper__permissions__name'])
            continue

        menu_tpl = {
            'id': item['pteamper__permissions__id'],
            'title': item['pteamper__permissions__name'],
            'name': item['pteamper__permissions__name'],
            'path': item['pteamper__permissions__url'].lstrip('/'),
            'menu_gp_id': item['pteamper__permissions__menu_gp_id'],
            'pid': item['pteamper__permissions__group__menu_id'],
            'menu_title': item['pteamper__permissions__group__menu__name'],
        }
        menu_permission_list.append(menu_tpl)
    # print('222222',menu_permission_list)
    for item in menu_permission_list:
        menu_dic = {}
        if item['pid'] in ret_dic.keys():
            ret_dic[item['pid']]['nextItem'].append(item)
        else:
            menu_dic['id']=item['id']
            menu_dic['name']=item['menu_title']
            menu_dic['title']=item['menu_title']
            menu_dic['nextItem']=[item,]
            ret_dic[item['pid']] = menu_dic

    return ret_dic




def rest_init_auth(user,request):
    auth_permission_list = []
    ret_dic={}
    permission_list = rest_init_permission(user, request)
    for item in permission_list:
        auth_tpl = {
            'id': item['pteamper__permissions__id'],
            'title': item['pteamper__permissions__name'],
            'name': item['pteamper__permissions__name'],
            'path': item['pteamper__permissions__url'],
            'menu_gp_id': item['pteamper__permissions__menu_gp_id'],
            'pid': item['pteamper__permissions__group__menu_id'],
            'menu_title': item['pteamper__permissions__group__menu__name'],
        }
        # 用于权限使用
        auth_permission_list.append(auth_tpl)
    for item in auth_permission_list:
        menu_dic = {}
        if item['pid'] in ret_dic.keys():
            ret_dic[item['pid']]['nextItem'].append(item)
        else:
            menu_dic['id']=item['id']
            menu_dic['name']=item['menu_title']
            menu_dic['title']=item['menu_title']
            menu_dic['nextItem']=[item,]
            ret_dic[item['pid']] = menu_dic

    return auth_permission_list



