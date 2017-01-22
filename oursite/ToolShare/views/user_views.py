from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.template import RequestContext, context
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login
from datetime import *
from django.db.models import Q

from ToolShare.models import Registrant, ShareZone, Shed, Notification, BorrowTool, Tool
from ToolShare.forms import CustomUserChangeForm, CustomUserCreationForm, CustomUserLoginForm, CustomUserPasswordChange



def user_status(request):
    return render(request, 'ToolShare/register-user-status.html', context_instance=RequestContext(request))

def update_user(request):
    if request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    template_name = 'ToolShare/myprofile.html'
    user = get_object_or_404(Registrant, pk=request.user.pk)
    form = CustomUserChangeForm(request.POST or None, instance=user)
    if form.is_valid():
        user = form.save(commit=False)
        user.edited = 1
        user.save()
        return redirect('/ToolShare')
    else:
        form_errors = form.errors
        #print(form_errors)
    print('not valid')
    return render(request, template_name, {'form': form,'user':user})

def add_user(request):
    if request.POST:
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            zipcode = (request.POST.get('zipcode'))

            user = form.save(commit=False)
            user.role='BAS'
            user.approval_status = 'Pending'
            user.edited=1
            user.save()

            try:
                sharezone = ShareZone.objects.get(zip_code=zipcode)
                print(sharezone)
            except ShareZone.DoesNotExist:
                sharezone = None
            if sharezone:
                print("share zone exists")
                user.sharezone = sharezone
                #sharezone.save()
                user.save()

                notificationObject = Notification()
                coordinators = user.get_shed().get_shed_coordinators()
                recipients = []
                for coordinator in coordinators:
                    recipients.append(coordinator)
                notificationObject.sendNotification("User_Approval", recipients, {'userid': str(user.pk)})


                print("user added to sharezone")
            else:

                sz = ShareZone.objects.create()
                sz.name = "ShareZone_" + zipcode
                sz.description = "ShareZone_" + zipcode
                sz.zip_code = zipcode
                user.sharezone=sz

                sz.save()
                print("sharezone created. User added to sharezone")

                shed = Shed.objects.create()
                shed.name = "Shed_" + zipcode
                shed.description = "Shed_" +zipcode
                shed.address = "Shed Address_" +zipcode
                #shed.zip_code = zipcode
                shed.save()
                shed.sharezone = sz
                shed.save()
                print("shed created. User assigned as shed coordinator")

                user.role='SHD'
                user.approval_status = 'Approved'
                user.edited=1
                user.save()
                print("added user as shed coordinator")

                notificationObject = Notification()
                recipients = []
                recipients.append(user.pk)
                notificationObject.sendNotification("Update_Shed", recipients, {'userid': str(user.pk)})

            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/ToolShare/register-user-status/')
        else:
            form_errors = form.errors
            print(form_errors)
    else:
        form = CustomUserCreationForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('ToolShare/register-user.html', args, context_instance=RequestContext(request))


def signin(request):
    template_name = 'ToolShare/login.html'
    form = CustomUserLoginForm(data=request.POST or None)
    if request.POST:
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    print("active user")
                    login(request, user)
                    print("valid user")
                    return HttpResponseRedirect('/ToolShare/')

    form_errors = form.errors
    print(form_errors)
    return render(request,template_name,{'form': form},context_instance=RequestContext(request))


def passwordchange(request):
    if request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    template_name = 'ToolShare/password-change.html'
    user = get_object_or_404(Registrant, pk=request.user.pk)
    form = CustomUserPasswordChange(user=user, data=request.POST or None)
    if request.POST:
        if form.is_valid():
            password = form.cleaned_data['new_password1']
            user.set_password(password)
            user.edited = 1
            user.save()
            print('form saved')
            return redirect('/ToolShare/logout')
        else:
            form_errors = form.errors
            print(form_errors)
            print('form errors')

    return render(request, template_name, {'form': form})

def view_exit_sharezone(request):
    '''
    Rules that prevent exiting a sharezone
    1. Registrant should not have any tools borrowed i.e. requests for which currently_borrowed=True
    2. Registrant should not have owned tools that are in the borrowed state
    3. Registrant exiting is the shed_coordinator of the shed/sharezone

    Notify users that have requested tools from this user that the user has left the sharezone ?
    '''
    errors = []
    tools_borrowed = BorrowTool.objects.filter(borrowerId = request.user.pk)
    tools_borrowed = tools_borrowed.filter(currently_borrowed=True)

    owned_tools = Tool.objects.filter(tool_owner = request.user.pk)
    borrowed_owned_tools = 0;

    if request.POST:
        # for tool in owned_tools:
        #     if BorrowTool.objects.get(toolId=tool.pk) and borrowed_owned_tools == 0:
        #         errors.append("You have tool(s) in the community that have been borrowed. Please make sure you have them back before you exit !")
        #         borrowed_owned_tools = 1
        #
        # if tools_borrowed is not None:
        #     errors.append("Please return the tools you have borrowed before leaving the community")

        if request.user.role == 'SHD':
            errors.append(
                "You are the shed coordinator for this community. You cannot leave the sharezone until you have this role !")

        if request.user.is_currently_borrowing_tools():
            errors.append("Please return the tools you have borrowed before leaving the community")

        for tool in owned_tools:
            currently_borrowed_owned_tools = BorrowTool.objects.filter(toolId=tool.pk).filter(currently_borrowed=True)
            if len(currently_borrowed_owned_tools) > 0 and borrowed_owned_tools == 0:
                errors.append("You have tool(s) in the community that have been borrowed. Please make sure you have them back before you exit !")
                borrowed_owned_tools = 1


        if len(errors) == 0:
            new_zip = (request.POST.get('zipcode'))
            user_exiting = request.user
            try:
                sharezone = ShareZone.objects.get(zip_code=new_zip)
                print(sharezone)
            except ShareZone.DoesNotExist:
                sharezone = None
            if sharezone:
                user_exiting.sharezone = sharezone
                #sharezone.save()
                user_exiting.save()
            else:
                sz = ShareZone.objects.create()
                sz.name = "ShareZone_" + new_zip
                sz.description = "ShareZone_" + new_zip
                sz.zip_code = new_zip
                user_exiting.sharezone = sz

                sz.save()
                print("sharezone created. User added to sharezone")

                shed = Shed.objects.create()
                shed.name = "Shed_" + new_zip
                shed.description = "Shed_" + new_zip
                shed.address = "Shed Address_" + new_zip
                # shed.zip_code = zipcode
                # shed.save()
                shed.sharezone = sz
                shed.save()
                print("shed created. User assigned as shed coordinator")

                user_exiting.role = 'SHD'
                user_exiting.approval_status = 'Approved'
                user_exiting.edited = 1
                user_exiting.save()
                print("added user as shed coordinator")
            return redirect('/ToolShare/logout')
    if errors is not None:
        args = {'errors': errors}
    else:
        args = {'errors': []}
    args.update(csrf(request))
    return render(request, 'ToolShare/exit-sharezone.html', args,context_instance=RequestContext(request))






