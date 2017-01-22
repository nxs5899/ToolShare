from ToolShare.models import Tool, Registrant, ShareZone, Shed, ToolLocation, ToolCategory, ToolCondition, ToolStatus
from ToolShare.forms import AdminCreateForm
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from datetime import *
from random import *
import string
import random


'''
This is an error page
'''
def error(request):
    args = {}
    return render(request, 'ToolShare/admin-error-permission.html', args, context_instance=RequestContext(request))

'''
This view is utilized to create a system admin
'''
def create_admin(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and request.user.role == 'SYS':

        if request.POST:
            form = AdminCreateForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.role = 'SYS'
                user.edited = 1
                user.save()
                return HttpResponseRedirect('/ToolShare/admin/view-admins/')
        else:
            form = AdminCreateForm()

        args = {}
        args['form'] = form
        return render(request, 'ToolShare/admin-create.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')


'''
This view is utilized to:
    1. display all sys admins on a GET request
    2. deletes a sys admin on a POST request
'''
def view_admins(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and request.user.role == 'SYS':

        all_admins = Registrant.objects.filter(role='SYS')
        args = {'admins': all_admins}

        if request.POST:
            adminId = request.POST.get('adminId')
            # a user cannot delete himself
            if adminId != request.user.pk:
                sys_admin = get_object_or_404(Registrant, pk=adminId)
                sys_admin.delete()

        return render(request, 'ToolShare/admin-view.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')


def edit_admin(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and request.user.role == 'SYS':

        all_admins = Registrant.objects.filter(role='SYS')
        args = {'admins': all_admins}

        if request.POST:
            adminId = request.POST.get('adminId')

            if adminId != '':
                user = get_object_or_404(Registrant, pk=adminId)
                user.first_name = request.POST.get('adminFirstName')
                user.last_name = request.POST.get('adminLastName')
                user.edited = 1
                user.save()

            return HttpResponseRedirect('/ToolShare/admin/view-admins/')

    return HttpResponseRedirect('/ToolShare/admin/error/')


'''
This view is utilized to:
    1. display all user (except sys admins) on a GET request
    2. deletes a user on a POST request
'''
def view_delete_users(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):

        '''Get all users, except the current user'''
        all_users = Registrant.objects.filter(is_deleted = False).exclude(pk=request.user.pk).exclude(role='SYS')
        deleted_users = Registrant.objects.filter(is_deleted=True).exclude(pk=request.user.pk).exclude(role='SYS')

        '''If the user is a Shed Admin, then exclude sys admins and users who belong to other zip's '''
        if request.user.role == 'SHD':
            all_users = Registrant.filter_by_zip_code(request.user.get_zip_code()).exclude(role='SYS').filter(is_deleted=False)
            deleted_users = Registrant.filter_by_zip_code(request.user.get_zip_code()).exclude(role='SYS').filter(is_deleted=True)

        '''must be 18+'''
        age_check = datetime.today() - timedelta(days=(365.2425*18.0))

        args = {'users': all_users, 'dob_max': age_check, 'deleted_users': deleted_users}

        if request.POST:
            userId = request.POST.get('userId')
            # a user cannot delete himself
            if userId != request.user.pk:
                user = get_object_or_404(Registrant, pk=userId)
                user.delete_user()

        return render(request, 'ToolShare/admin-manage-users.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')


'''
This view is utilized to:
    1. Edit the properties of an existing user
    2. Add a new user
'''
#TODO - need to work on change of zip and role
def add_edit_user(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):
        if request.POST:
            userId = request.POST.get('userId')

            if userId != '':
                user = get_object_or_404(Registrant, pk=userId)
                user.first_name = request.POST.get('userFirstName')
                user.last_name = request.POST.get('userLastName')
                user.date_of_birth = request.POST.get('userDOB')
                user.address_line1 = request.POST.get('userAddressLine1')
                user.address_line2 = request.POST.get('userAddressLine2')
                user.telephone = request.POST.get('userTelephone')
                user.approval_status = request.POST.get('userApprovalStatus')
                if user.approval_status == 'Rejected':
                    user.is_deleted = True
                role = request.POST.get('userRole')
                if (role == 'Basic User'):
                    user.role='BAS'
                if (role == 'Shed Coordinator'):
                    user.role='SHD'
                if (role == 'System Administrator'):
                        user.role = 'SYS'

                user.edited = 1
                user.save()
            else:
                user = Registrant()
                user.first_name = request.POST.get('userFirstName')
                user.last_name = request.POST.get('userLastName')
                user.date_of_birth = request.POST.get('userDOB')
                user.address_line1 = request.POST.get('userAddressLine1')
                user.address_line2 = request.POST.get('userAddressLine2')
                user.telephone = request.POST.get('userTelephone')
                user.approval_status = request.POST.get('userApprovalStatus')
                if user.approval_status == 'Rejected':
                    user.is_deleted = True
                user.save()

        return HttpResponseRedirect('/ToolShare/admin/manage-users/')

    return HttpResponseRedirect('/ToolShare/admin/error/')

def restore_user(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):
        if request.POST:
            userId = request.POST.get('userId')

            if userId != '':
                user = get_object_or_404(Registrant, pk=userId)
                user.restore_user()

        return HttpResponseRedirect('/ToolShare/admin/manage-users/')

    return HttpResponseRedirect('/ToolShare/admin/error/')

'''
This view is utilized to reset the password of a user
The user id must be part of the url
'''
def password_reset(request, userId):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):
        if userId != '':
            userObject = get_object_or_404(Registrant, pk=userId)

            '''A shed coordinator cannot rest the password of a user in a different shed'''
            if request.user.role == 'SHD' and userObject.get_zip_code() != request.user.get_zip_code():
                return HttpResponseRedirect('/ToolShare/admin/error/')

            #characters = string.ascii_letters + string.punctuation + string.digits
            #new_password = "".join(choice(characters) for x in range(randint(8, 8)))

            characters = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
            new_password = "".join(random.sample(characters, 8))

            userObject.set_password(new_password)
            #userObject.edited = 1
            userObject.save()

            args = {'userObject': userObject, 'new_password': new_password}

            return render(request, 'ToolShare/admin-user-password-reset.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')



'''
This view is utilized to:
    1. display all tools on a GET request
    2. deletes a tool on a POST request
'''
def view_delete_tools(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):

        if request.POST:
            toolId = request.POST.get('toolId')
            tool = get_object_or_404(Tool, pk=toolId)
            tool.delete_tool()

        all_tools = Tool.objects.filter(is_deleted = False)
        all_deleted_tools = Tool.objects.filter(is_deleted=True)
        tool_locations = ToolLocation.objects.all()
        tool_categories = ToolCategory.objects.all()
        tool_conditions = ToolCondition.objects.all()
        tool_statuses = ToolStatus.objects.all()

        '''Users are required to populate the dropdown in add/edit mode'''
        '''Get all users, except the current user & sys admins'''
        all_users = Registrant.objects.all().exclude(role='SYS').filter(is_deleted=False)

        '''If the user is a Shed Admin, then include only tools in the users zipcode '''
        if request.user.role == 'SHD':

            all_tools = Tool.filter_by_zip_code(request.user.get_zip_code())
            all_deleted_tools = Tool.filter_deleted_tools_by_zip_code(request.user.get_zip_code())
            #all_tools = all_tools.filter(tool_owner__zipcode=request.user.get_zip_code())
            #all_users = all_users.filter(zipcode=request.user.get_zip_code())
            all_users = Registrant.filter_by_zip_code(request.user.get_zip_code()).filter(is_deleted=False)

        args = {'users': all_users, 'tools': all_tools, 'deletedTools': all_deleted_tools, 'locations': tool_locations, 'categories': tool_categories, 'conditions': tool_conditions, 'statuses': tool_statuses}



        return render(request, 'ToolShare/admin-manage-tools.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')


'''
This view is utilized to:
    1. Edit the properties of an existing tool
    2. Add a new tool
'''
def add_edit_tool(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):
        if request.POST:
            toolId = request.POST.get('toolId')

            #TODO - need to handle the flow if a tool status is changed to/from Borrowed
            if toolId != '':
                tool = get_object_or_404(Tool, pk=toolId)
                tool.name = request.POST.get('toolName')
                tool.description = request.POST.get('toolDescription')
                tool.instructions = request.POST.get('toolInstructions')
                tool.tool_category = ToolCategory.objects.get(category_name=request.POST.get('toolCategory'))
                tool.tool_condition = ToolCondition.objects.get(condition_name=request.POST.get('toolCondition'))
                tool.tool_location = ToolLocation.objects.get(location_name=request.POST.get('toolLocation'))
                user = get_object_or_404(Registrant, email=request.POST.get('toolOwner'))
                tool.tool_owner = user
                tool.edited = 1
                tool.save()
            else:
                tool = Tool()
                tool.name = request.POST.get('toolName')
                tool.description = request.POST.get('toolDescription')
                tool.instructions = request.POST.get('toolInstructions')
                tool.tool_category = ToolCategory.objects.get(category_name=request.POST.get('toolCategory'))
                tool.tool_condition = ToolCondition.objects.get(condition_name=request.POST.get('toolCondition'))
                tool.tool_location = ToolLocation.objects.get(location_name=request.POST.get('toolLocation'))
                tool.tool_status = ToolStatus.objects.get(status_name='Available')
                user = get_object_or_404(Registrant, email=request.POST.get('toolOwner'))
                tool.tool_owner = user
                tool.save()


        return HttpResponseRedirect('/ToolShare/admin/manage-tools/')


    return HttpResponseRedirect('/ToolShare/admin/error/')


def restore_tool(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS' or request.user.role == 'SHD'):
        if request.POST:
            toolId = request.POST.get('toolId')

            if toolId != '':
                tool = get_object_or_404(Tool, pk=toolId)
                tool.restore_tool2()

        return HttpResponseRedirect('/ToolShare/admin/manage-tools/')


    return HttpResponseRedirect('/ToolShare/admin/error/')

'''
This view is utilized to:
    1. display all share zones on a GET request
    2. deletes a share zone on a POST request
'''
def view_delete_share_zones(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS'):
        all_share_zones = ShareZone.objects.all()
        distinct_zip = all_share_zones.filter().values('zip_code').distinct()

        args = {'share_zones': all_share_zones, 'existing_zip': distinct_zip}

        if request.POST:
            sharezoneId = request.POST.get('sharezoneId')
            share_zone = get_object_or_404(ShareZone, pk=sharezoneId)
            share_zone.delete()

        return render(request, 'ToolShare/admin-manage-share-zones.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')


'''
This view is utilized to:
    1. Edit the properties of an existing share zone
    2. Add a new share zone and shed
'''
def add_edit_share_zone(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS'):
        if request.POST:
            zoneId = request.POST.get('zoneId')

            if zoneId != '':
                zone = get_object_or_404(ShareZone, pk=zoneId)
                zone.description = request.POST.get('zoneDescription')
                zone.edited=1
                zone.save()
            else:
                zone = ShareZone()
                zone.zip_code = request.POST.get('zoneZip')
                zone.description = request.POST.get('zoneDescription')
                zone.name = "ShareZone_"+request.POST.get('zoneZip')
                zone.save()

                shed = Shed()
                shed.name = "Shed_"+request.POST.get('zoneZip')
                shed.description = "Shed_"+request.POST.get('zoneZip')
                shed.address = "Shed Address_"+request.POST.get('zoneZip')
                shed.zip_code = request.POST.get('zoneZip')
                shed.save()

        return HttpResponseRedirect('/ToolShare/admin/manage-share_zones/')


    return HttpResponseRedirect('/ToolShare/admin/error/')

'''
This view is utilized to:
    1. display all sheds on a GET request
    2. deletes a shed on a POST request
'''
def view_delete_sheds(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and request.user.role == 'SYS':
        all_sheds = Shed.objects.all()
        args = {'sheds': all_sheds}

        if request.POST:
            shedId = request.POST.get('shedId')
            shed = get_object_or_404(Shed, pk=shedId)
            shed.delete()

        return render(request, 'ToolShare/admin-manage-sheds.html', args, context_instance=RequestContext(request))

    return HttpResponseRedirect('/ToolShare/admin/error/')

'''
This view is utilized to:
    1. Edit the properties of an existing share zone
    2. Add a new share zone and shed
'''
def add_edit_shed(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is not None and (request.user.role == 'SYS'):
        if request.POST:
            shedId = request.POST.get('shedId')

            if shedId != '':
                shed = get_object_or_404(Shed, pk=shedId)
                shed.description = request.POST.get('shedDescription')
                shed.address = request.POST.get('shedAddress')
                shed.edited = 1
                shed.save()
            else:
                shed = ShareZone()
                shed.description = request.POST.get('shedDescription')
                shed.name = "Shed_"+request.POST.get('shedZip')
                shed.address = "Shed Address_"+request.POST.get('shedAddress')
                shed.save()

        return HttpResponseRedirect('/ToolShare/admin/manage-sheds/')


    return HttpResponseRedirect('/ToolShare/admin/error/')