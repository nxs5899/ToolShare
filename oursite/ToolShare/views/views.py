from django.shortcuts import render, render_to_response

from ToolShare.forms import Approve_Request
from ToolShare.models import Tool, Registrant, BorrowTool, ShareZone, Shed, Notification, ToolStatus, BlackoutTool, ToolCondition
from ToolShare.forms import ToolForm, CustomUserChangeForm, CustomUserCreationForm, CustomUserLoginForm, \
    CustomUserPasswordChange, BorrowToolForm, ToolUpdate, ReturnToolForm, UpdateShedForm, BlackoutToolForm
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.contrib.auth import authenticate, login

from django.template import RequestContext, context
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group

import datetime

from django.db.models import Q

from ToolShare.models import ToolLocation

def index(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.user.pk is None or request.user.role == 'SYS':
        args = {'tool':''}
    else:
        sharezone = request.user.sharezone
        shed_zip = sharezone.zip_code
        if shed_zip is None or shed_zip =='':
            args = {'tool': ''}
            return render(request, 'ToolShare/index.html', args, context_instance=RequestContext(request))

        shed = Shed.objects.get(sharezone=sharezone)
        if shed is None:
            args = {'tool': ''}
            return render(request, 'ToolShare/index.html', args, context_instance=RequestContext(request))

        borrowed_tools = BorrowTool.objects.exclude(currently_borrowed=False)
        borrowed_tools = borrowed_tools.filter(borrowerId=request.user.pk)

        shed_tool = Tool.filter_by_zip_code(sharezone.zip_code)[:5]

        args = {'tool':  Tool.objects.filter(tool_owner=request.user.pk).order_by('name')[:5],
                'shed_tool': shed_tool,
                'borrowed_tool': borrowed_tools[:5]}


    return render(request, 'ToolShare/index.html', args, context_instance=RequestContext(request))

def ApproveRequest(request, requestId):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    BorrowRequestObject = BorrowTool.objects.filter(pk=requestId)
    if BorrowRequestObject.count()<=0:
        args = {'NoBorrowRequest': 'true'}
        return render(request, 'ToolShare/Approve_Borrow.html', args, context_instance=RequestContext(request))


    BorrowRequest = BorrowTool.objects.get(pk=requestId)
    #form = Approve_Request(request.GET, instance=BorrowRequest)
    args = {'BorrowerId': BorrowRequest.borrowerId,
            'ToolId':BorrowRequest.toolId ,
            'StartDate': BorrowRequest.start_date,
            'EndDate' : BorrowRequest.end_date,
            'BorrowRequestId':requestId,
            'BorrowerNotes':BorrowRequest.borrower_notes,
            'NoBorrowRequest': 'false',
            'obj':BorrowRequest
            }
    if request.POST:

        #form = Approve_Request(request.POST)
        BorrowRequest = get_object_or_404(BorrowTool, pk=requestId)
        #BorrowRequest.currently_borrowed=True
        #BorrowRequest.edited=1
        #BorrowRequest.save()

        BorrowerID=(request.POST.get('borrowerId2'))

        if BorrowerID is not None and BorrowerID!='':
            notification = Notification()
            recipient = Registrant.objects.get(pk=BorrowerID)
            if recipient is not None:
                recipients = [recipient]
                notification.sendNotification("Borrow_Request_Confirmed", recipients,{'toolid':BorrowRequest.toolId.id})
           # return HttpResponseRedirect('/ToolShare/my-tools')

        RequestId = (request.POST.get('BorrowRequestId'))
        print (RequestId)
        if RequestId is not None and RequestId != '':
            Request_to_delete = get_object_or_404(BorrowTool, pk=RequestId)
            notification = Notification()
            recipients =  [BorrowRequest.borrowerId]
            notification.sendNotification("Borrow_Request_Rejected", recipients, {'toolid':BorrowRequest.toolId.id})
            Request_to_delete.delete()

            toolObject = Tool.objects.get(pk = BorrowRequest.toolId.id)
            available_status = ToolStatus.objects.get(status_name='Available')
            toolObject.tool_status = available_status
            toolObject.save()




        return HttpResponseRedirect('/ToolShare/my-tools')

    return render(request, 'ToolShare/Approve_Borrow.html',args, context_instance=RequestContext(request))

def view_return_tools(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    '''
    1. Get the user object (person who is going to return the tool
    ---GET Request---
    2. Get the list of tools the user has borrowed
        2a - Query BorrowTool where borrowerId == user id && today is between the start and end date (both inclusive)/currently_borrowed == True
        2b - Query Tool for list of tool objects based on results of 2a
    ---Post Request I- Return currently borrowed tools--
    3a. Change the status of the selected tool to 'Available' (Tool.tool_status')
    3b. Change the status in the borrow model to false (BorrowTool.currently_borrowed == True)
    3c. Update BorrowTool.return_date to today
    ---Post Request II- cancel future requests--
    4a. Remove the request for the Tool from the Borrow Tool model
        Tool status does not eed to be updated - tool was Available
    '''

    ensure_correct_tool_availability_status()
    current_user = get_object_or_404(Registrant, pk=request.user.pk)
    form = ReturnToolForm()

    today = datetime.date.today()
    borrowed_tools = BorrowTool.objects.filter(borrowerId=request.user.pk)
    borrowed_tools = borrowed_tools.filter(currently_borrowed=True)
    print(borrowed_tools)
    future_requests = BorrowTool.objects.filter(borrowerId = request.user)
    future_requests = future_requests.filter(start_date__gt=today)

    args = {'tool_list': borrowed_tools, 'current_user':current_user, 'form':form,'future_requests':future_requests, 'selectedTool':''}

    if request.POST:
        form = ReturnToolForm(request.POST)

        selectedToolId = (request.POST.get('toolId'))
        borrowId = (request.POST.get('borrowId'))

        if selectedToolId is not None and borrowId is not None:
            '''
            Status of the tool will be set to Available only when the return is acknowledged
            BorrowTool object/ request again will be updated after the return is acknowledged
            '''

            tool = get_object_or_404(Tool, pk=str(selectedToolId))
            print(tool)
            print(selectedToolId)
            print(borrowId)
            notification = Notification()
            print(tool.tool_location)
            if tool.tool_location.location_name == 'Home':
                print("In here")
                recipients = [tool.tool_owner]
                args={'toolid':selectedToolId,'userid':request.user.pk,'borrow_request':borrowId}
                notification.sendNotification('Tool_Returned_Home',recipients,args)
                print("Notification sent")
            if tool.tool_location.location_name == 'Shed':
                shed = tool.get_shed()
                coordinators = []
                shed_coordinators = shed.get_shed_coordinators()
                for coordinator in shed_coordinators:
                    coordinators.append(coordinator)
                recipients = coordinators
                args = {'toolid': selectedToolId, 'userid': request.user.pk, 'borrow_request': borrowId}
                notification.sendNotification('Tool_Returned_Shed', recipients, args)
                print("Notification sent")
            return HttpResponseRedirect('/ToolShare/')

        # # Update Tool Status
        # tool_status = ToolStatus.objects.get(status_name='Available')
        # selectedToolId = (request.POST.get('toolId'))
        # print(selectedToolId)
        # if selectedToolId is not None:
        #     print(selectedToolId)
        #     tool = get_object_or_404(Tool, pk=str(selectedToolId))
        #     tool.tool_status = tool_status
        #     tool.edited = 1
        #     tool.save()
        #     print(tool.tool_status)

        # Update the BorrowTool model
        # borrowId = (request.POST.get('borrowId'))
        # if borrowId is not None:
        #     borrowed_tool = BorrowTool.objects.get(pk=str(borrowId))  # BorrowTool.objects.filter(pk=args)
        #     borrowed_tool.currently_borrowed = False
        #     borrowed_tool.return_date = datetime.today().date()
        #     borrowed_tool.edited = 1
        #     borrowed_tool.save()


            # render(request, 'ToolShare/return_tool.html', args, context_instance=RequestContext(request))
            # return HttpResponseRedirect('/ToolShare/my-tools')

        # Delete future borrowing request if any request is cancelled
        futureRequestId = (request.POST.get('request_id'))
        if futureRequestId != '' and futureRequestId != None:
            futureRequest_to_delete = get_object_or_404(BorrowTool, pk=futureRequestId)
            futureRequest_to_delete.delete()

    return render(request, 'ToolShare/return_tool.html', args, context_instance=RequestContext(request))

def view_borrow_tool(request, toolId):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    ensure_correct_tool_availability_status()

    today = datetime.date.today()
    FutureBorrowToolObject = BorrowTool.objects.filter(toolId__pk=toolId).filter(return_date=None).filter(start_date__gte=today)

    BlackoutDateRange = BlackoutTool.objects.filter(toolId__pk=toolId).filter(start_date__gte=today)


    tool = get_object_or_404(Tool, pk=toolId)
    if request.POST:
        form = BorrowToolForm(request.POST)

        # Rules that prevent a tool from being borrowed
        if tool is None:
            form.add_error(None, "The selected tool does not exist.")
        if tool.tool_owner_id == request.user.id:
            form.add_error(None, "You cannot borrow a tool that you own.")


        '''
        Disallow future borrowing when
            1. Start and end dates are after start and end dates of an existing request
            2. Start and end dates are before start and end dates of an existing request
            3. Start and end dates fall between start and end dates of an existing request
            4. Start and end dates exactly overlap start and end dates of an existing request
            5. Start and end dates are before and after start and end dates of an existing request
        '''
        future_borrow_requests_for_tool = BorrowTool.objects.filter(toolId=tool)
        form.is_valid()
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        today = datetime.date.today()
        overlapping_requests_case1 = future_borrow_requests_for_tool.filter(start_date__lt=start_date,end_date__gt=start_date,end_date__lt=end_date)
        overlapping_requests_case2 = future_borrow_requests_for_tool.filter(start_date__gt=start_date,end_date__gt=end_date, start_date__lt=end_date)
        overlapping_requests_case3 = future_borrow_requests_for_tool.filter(start_date__lt=start_date, end_date__gt=end_date)
        overlapping_requests_case4 = future_borrow_requests_for_tool.filter(start_date=start_date,end_date=end_date)
        overlapping_requests_case5 = future_borrow_requests_for_tool.filter(start_date__gt=start_date,end_date__lt=end_date)
        overlapping_requests_case6 = future_borrow_requests_for_tool.filter(start_date__lte=start_date, end_date__gte=end_date)
        overlapping_requests_case7 = future_borrow_requests_for_tool.filter(start_date=start_date)
        overlapping_requests_case8 = future_borrow_requests_for_tool.filter(end_date=end_date)
        overlapping_requests_case9 = future_borrow_requests_for_tool.filter(end_date=start_date)
        overlapping_requests_case10 = future_borrow_requests_for_tool.filter(start_date=end_date)

        if overlapping_requests_case1.count() or overlapping_requests_case2.count() or overlapping_requests_case3.count() \
                or overlapping_requests_case4.count() or overlapping_requests_case5.count() \
            or overlapping_requests_case6.count() or overlapping_requests_case7.count() \
                or overlapping_requests_case8.count() or overlapping_requests_case9.count() or overlapping_requests_case7.count():
            form.add_error(None, "Sorry the tool has already been borrowed during the requested period")

        '''
               Disallow future borrowing when
                   1. Start and end dates are after start and end dates of a blackout period
                   2. Start and end dates are before start and end dates of a blackout period
                   3. Start and end dates fall between start and end dates of a blackout period
                   4. Start and end dates exactly overlap start and end dates of a blackout period
                   5. Start and end dates are before and after start and end dates of a blackout period
        '''
        blackout_periods_for_tool = BlackoutTool.objects.filter(toolId=tool)
        overlapping_blackout_requests_case1 = blackout_periods_for_tool.filter(start_date__lt=start_date,end_date__gt=start_date, end_date__lt=end_date)
        overlapping_blackout_requests_case2 = blackout_periods_for_tool.filter(start_date__gt=start_date,end_date__gt=end_date, start_date__lt=end_date)
        overlapping_blackout_requests_case3 = blackout_periods_for_tool.filter(start_date__lt=start_date,end_date__gt=end_date)
        overlapping_blackout_requests_case4 = blackout_periods_for_tool.filter(start_date=start_date, end_date=end_date)
        overlapping_blackout_requests_case5 = blackout_periods_for_tool.filter(start_date__gt=start_date,end_date__lt=end_date)
        overlapping_blackout_requests_case6 = blackout_periods_for_tool.filter(start_date__lte=start_date, end_date__gte=end_date)
        overlapping_blackout_requests_case7 = blackout_periods_for_tool.filter(start_date=start_date)
        overlapping_blackout_requests_case8 = blackout_periods_for_tool.filter(end_date=end_date)
        # overlapping_blackout_requests_case8 = blackout_periods_for_tool.filter(end_date__lte=end_date,start_date__lte=start_date)
        overlapping_blackout_requests_case9 = blackout_periods_for_tool.filter(end_date=start_date)
        overlapping_blackout_requests_case10 = blackout_periods_for_tool.filter(start_date=end_date)


        if overlapping_blackout_requests_case1.count() or overlapping_blackout_requests_case2.count() or \
                overlapping_blackout_requests_case3.count() or overlapping_blackout_requests_case4.count() or overlapping_blackout_requests_case5.count() \
                or overlapping_blackout_requests_case6.count() or overlapping_blackout_requests_case7.count() or \
                overlapping_blackout_requests_case8.count() or overlapping_blackout_requests_case9.count() or overlapping_blackout_requests_case10.count():
            form.add_error(None, "Sorry the tool has been blacked out during the requested period. Try changing the start and end dates..")

        if form.is_valid():
            borrow_tool = form.save(commit=False)
            borrow_tool.save()
            borrow_request = BorrowTool.objects.get(id=borrow_tool.id)
            print("Borrower : ")
            print (borrow_request.borrowerId)
            tool.edited = 1
            tool.save()
            print(tool.tool_status)
            toolLocation = ToolLocation.objects.get(location_name='Shed')
            if tool.tool_location != toolLocation:
                notification = Notification()
                recipients = [tool.tool_owner]
                #notification.sendNotification("Borrow_Request", toolId, recipients)
                notification.sendNotification("Borrow_Request", recipients,{'borrow_request':str(borrow_tool.id),'toolid':toolId})
            else:
                notification = Notification()
                sharezone = request.user.sharezone
                #shed_zip = sharezone.zip_code
                shed_coordinators = Registrant.objects.filter(role="SHD")
                shed_coordinators = shed_coordinators.filter(sharezone=sharezone)
                recipients = shed_coordinators
                notification.sendNotification("Borrow_Shed", recipients, {'borrowerid':str(borrow_tool.borrowerId.pk),'toolid':toolId})
            return HttpResponseRedirect('/ToolShare/shed/return-tools/')
        else:
            form_errors = form.errors
            print(form_errors)
    else:
        form = BorrowToolForm()

    if tool is not None:
        args = {'tool': tool}
    else:
        args = {'tool': ''}
    args.update(csrf(request))
    args['form'] = form
    args['FutureBorrowToolObject'] = FutureBorrowToolObject
    args['BlackoutDateRange'] = BlackoutDateRange
    return render(request, 'ToolShare/tool-borrow.html', args, context_instance=RequestContext(request))

def view_tools(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    ensure_correct_tool_availability_status()
    tools = Tool.objects.all()
    context = {'tools': tools}
    return render(request, 'ToolShare/view_tools.html', context, context_instance=RequestContext(request))

def view_shed_tools(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    ensure_correct_tool_availability_status()
    #shed = Shed.objects.get(zip_code=request.user.zipcode)
    sharezone  = request.user.sharezone
    shed = Shed.objects.get(sharezone=sharezone)
    #coordinators = ShedCoordinator.objects.filter(shed=shed)
    '''
    Get shed coordinators for this shed
        1. Get users with the 'SHD' role
        2. Filter users by sharezone
    '''
    shed_coordinators = shed.get_shed_coordinators()
    #shed_coordinators = Registrant.objects.filter(role="SHD")
    #shed_coordinators = shed_coordinators.filter(sharezone=sharezone)
    #tools = Tool.objects.filter(shed=shed)
    tools = Tool.filter_by_zip_code(sharezone.zip_code)

    for tool in tools:
        print (tool.name + "-" +tool.tool_status.status_name)
    context = {'tools':tools, 'shed':shed, 'coordinators':shed_coordinators}
    return render(request, 'ToolShare/shed-tools.html', context, context_instance = RequestContext(request))

def view_mytools(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    ensure_correct_tool_availability_status()
    tools = Tool.objects.filter(tool_owner=request.user.pk)
    toolId = (request.POST.get('toolId'))

    if toolId is not None:
        tool_to_delete = Tool.objects.get(pk=toolId)
        tool_to_delete.delete_tool()

    context = {'tools':tools}
    return render(request, 'ToolShare/my-tools.html', context, context_instance=RequestContext(request))

def view_update_tool(request, toolId):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    ensure_correct_tool_availability_status()
    tool = get_object_or_404(Tool, pk=toolId)

    if request.POST:
        form = ToolUpdate(request.POST, instance=tool)

        # Rules that prevent a tool from being edited
        if tool is None:
            form.add_error(None, "The selected tool does not exist.")
        if tool.tool_owner_id != request.user.id:
            form.add_error(None, "You cannot update a tool that you do now own.")
        borrowed_status = ToolStatus.objects.get(status_name='Borrowed')
        if tool.tool_status == borrowed_status:
            form.add_error(None,"This tool is currently borrowed and cannot be edited")


        if form.is_valid():
            tool = form.save(commit=False)

            tool_status_deactivated = ToolStatus.objects.get(status_name='Deactivated')
            if tool.tool_status==tool_status_deactivated:
                '''
                Changed the tool-update form to allow deactivation even if the status is borrowed since we will have to support
                borrowing in the future
                    1. Get borrow requests for this tool
                    2. Filter to get future requests (available now) OR filter by date
                    3. Get the borrowers of these future requests
                '''
                today = datetime.date.today()
                borrow_requests = BorrowTool.objects.filter(toolId=toolId)
                future_requests = borrow_requests.filter(Q(start_date__gte=today))

                borrowers = []
                for future_request in future_requests:
                    borrower = get_object_or_404(Registrant, pk=future_request.borrowerId.id)
                    borrowers.append(borrower)
                notification = Notification()

                recipients = borrowers
                notification.sendNotification('Tool_Deactivated',recipients,{'toolid':toolId})

            tool.save()
            return HttpResponseRedirect('/ToolShare/my-tools')
        else:
            form_errors = form.errors
            print(form_errors)

    else:
        form = ToolUpdate(instance=tool)

    if tool is not None:
        args = {'tool': tool}
    else:
        args = {'tool': ''}
    args.update(csrf(request))
    args['form'] = form
    return render(request, 'ToolShare/tool-update.html', args, context_instance=RequestContext(request))

def register_tool(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    if request.POST:
        form = ToolForm(request.POST)
        if form.is_valid():
            tool = form.save(commit=False)
            #userzip = request.user.zipcode
            sharezone = request.user.sharezone
            userzip = sharezone.zip_code
            shed = Shed.objects.get(name = "Shed_"+userzip)
            tool.shed = shed
            tool_status = ToolStatus.objects.get(status_name='Available')
            tool.tool_status = tool_status
            tool_owner = Registrant.objects.get(id=request.user.pk)
            tool.tool_owner = tool_owner
            tool.save()
            return HttpResponseRedirect('/ToolShare/my-tools')
    else:
        form = ToolForm()
    args = {}
    args.update(csrf(request))
    args['form']=form
    return render_to_response('ToolShare/register_tool.html', args, context_instance=RequestContext(request))


def show_notification(request):
    if request.user.pk is not None and request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    notifications = Notification.objects.filter(recipient = request.user.pk).order_by('-created_at')

    for notificationObject in notifications:
        notificationObject.viewed = True
        notificationObject.save()

    user = get_object_or_404(Registrant, pk=request.user.pk)
    return render_to_response('ToolShare/view-notifications.html', {'notifications':notifications, 'user':user})

'''
Sample script to set status of tools being borrowed in the future - Call when user tries to check status - view shed tools/borrow tools
    For all tools in the BorrowTool Model
        1. If Borrow Period begins today set status to Borrowed
            Exclude tools which are returned on the same day - their status must remain Available
        2. If borrow period ends today set status Available
'''


def ensure_correct_tool_availability_status():
    '''
    1. For all borrow requests that have a start_date of today set corresponding tool status = Borrowed
        Exclude tools that are returned on the same day
    2. For all borrow requests that have an end_date of today set corresponding tool status = Available
        Assuming tools are all returned on the end_date by default
        Exclude tools that have been returned before the end_date i.e. return_date < end_date
    3. For all blacked out tools if blackout period begins today set tool status = Blackout
    4. For all blacked out tools if blackout period ends today set tool status = Available
    '''

    tools_borrow_period_begins_today = BorrowTool.objects.filter(start_date=datetime.date.today())
    tools_borrow_period_begins_today = tools_borrow_period_begins_today.exclude(return_date=datetime.date.today())
    for borrow_request in tools_borrow_period_begins_today:
        print (borrow_request.start_date)
        borrow_request.currently_borrowed = True
        tool = Tool.objects.get(pk=borrow_request.toolId.id)
        borrowed_status = ToolStatus.objects.get(status_name='Borrowed')
        print ("Setting status to borrowed now !!!!")
        tool.tool_status = borrowed_status
        borrow_request.save()
        tool.save()

    tools_borrow_period_ends_today = BorrowTool.objects.filter(end_date=datetime.date.today() - datetime.timedelta(days=1))
    tools_borrow_period_ends_today = tools_borrow_period_ends_today.exclude(currently_borrowed=False)
    for borrow_request in tools_borrow_period_ends_today:
        #borrow_request.currently_borrowed = False
        tool = Tool.objects.get(pk=borrow_request.toolId.id)
        available_status = ToolStatus.objects.get(status_name='Available')
        tool.tool_status = available_status
        tool.save()

    blackout_period_begins_today = BlackoutTool.objects.filter(start_date =datetime.date.today())
    for blackout in blackout_period_begins_today:
        tool = Tool.objects.get(pk=blackout.toolId.id)
        blackedout_status = ToolStatus.objects.get(status_name='Blackout')
        tool.tool_status = blackedout_status
        tool.save()
    blackout_period_ends_today = BlackoutTool.objects.filter(end_date=datetime.date.today())
    for blackout in blackout_period_ends_today:
        tool = Tool.objects.get(pk=blackout.toolId.id)
        available_status = ToolStatus.objects.get(status_name='Available')
        tool.tool_status = available_status
        tool.save()

def view_blackout_tool(request, toolId):
    if request.user.approval_status != 'Approved':
        return HttpResponseRedirect('/ToolShare/register-user-status/')

    ensure_correct_tool_availability_status()
    tool = get_object_or_404(Tool,pk=toolId)
    if request.POST:

        form = BlackoutToolForm(request.POST)
        if tool is None:
            form.add_error(None, "The selected tool does not exist.")
        if tool.tool_owner_id != request.user.id:
            form.add_error(None, "You cannot set a blackout period for a tool you do not own.")
        available_status = ToolStatus.objects.get(status_name='Available')
        if tool.tool_status != available_status:
            form.add_error(None,"This tool needs to be available for setting a blackout period.")

        if form.is_valid():
            today = datetime.date.today()
            borrow_requests = BorrowTool.objects.filter(toolId=toolId)
            future_requests = borrow_requests.filter(start_date__gt=today)

            form.is_valid()
            blackout_start_date = form.cleaned_data['start_date']
            blackout_end_date = form.cleaned_data['end_date']

            overlapping_requests_case1 = future_requests.filter(start_date__lt=blackout_start_date,end_date__gt=blackout_start_date,end_date__lt=blackout_end_date)
            overlapping_requests_case2 = future_requests.filter(start_date__gt=blackout_start_date,end_date__gt=blackout_end_date,start_date__lt=blackout_end_date)
            overlapping_requests_case3 = future_requests.filter(start_date__lt=blackout_start_date,end_date__gt=blackout_end_date)
            overlapping_requests_case4 = future_requests.filter(start_date=blackout_start_date,end_date=blackout_end_date)
            overlapping_requests_case5 = future_requests.filter(start_date__gt = blackout_start_date, end_date__lt = blackout_start_date)

            borrowers = []
            if overlapping_requests_case1.count():
                for future_request in overlapping_requests_case1:
                    borrower = get_object_or_404(Registrant, pk=future_request.borrowerId.id)
                    borrowers.append(borrower)
            if overlapping_requests_case2.count():
                for future_request in overlapping_requests_case2:
                    borrower = get_object_or_404(Registrant, pk=future_request.borrowerId.id)
                    borrowers.append(borrower)
            if overlapping_requests_case3.count():
                for future_request in overlapping_requests_case3:
                    borrower = get_object_or_404(Registrant, pk=future_request.borrowerId.id)
                    borrowers.append(borrower)
            if overlapping_requests_case4.count():
                for future_request in overlapping_requests_case4:
                    borrower = get_object_or_404(Registrant, pk=future_request.borrowerId.id)
                    borrowers.append(borrower)
            if overlapping_requests_case5.count():
                for future_request in overlapping_requests_case5:
                    borrower = get_object_or_404(Registrant, pk=future_request.borrowerId.id)
                    borrowers.append(borrower)

            if borrowers:
                notification = Notification()
                recipients = borrowers
                notification.sendNotification('Tool_Blackout', recipients, {'toolid':toolId})

            form.save()
            return HttpResponseRedirect("/ToolShare/")
        else:
            form_errors = form.errors
            print (form_errors)
    else:
        form = BlackoutToolForm()

    if tool is not None:
        args = {'tool': tool}
    else:
        args = {'tool': ''}
    args.update(csrf(request))
    args['form'] = form
    return render(request, 'ToolShare/blackout_tool.html', args, context_instance=RequestContext(request))


def view_acknowledge_tool_return(request, requestId):
    tool_conditions = ToolCondition.objects.all()
    errors = []
    if request.POST:
        return_condition = request.POST.get('tool_condition')
        borrow_request = get_object_or_404(BorrowTool, pk=requestId)
        tool = get_object_or_404(Tool, pk=borrow_request.toolId.id)
        if return_condition is not None:
            if borrow_request is not None:
                #check if another shed coordinator has already acknowledged return
                print(tool.tool_location.location_name)
                print ( borrow_request.currently_borrowed)
                if tool.tool_location.location_name == 'Shed' and borrow_request.currently_borrowed == False:
                    errors.append("Another shed coordinator has already acknowledged this return. You may safely ignore this notification")
                print (borrow_request.return_condition)
                # update the request in the borrow tool model
                if len(errors) == 0:
                    condition = ToolCondition.objects.get(condition_name=return_condition)
                    borrow_request.return_condition = condition
                    borrow_request.currently_borrowed = False
                    borrow_request.return_date = datetime.date.today()
                    borrow_request.edited = 1
                    borrow_request.save()
                    print(borrow_request.return_condition)
                    #update the tool status
                    available_status = ToolStatus.objects.get(status_name='Available')
                    tool.tool_status = available_status
                    tool.tool_condition = condition
                    tool.edited = 1
                    tool.save()
                    return HttpResponseRedirect("/ToolShare/")
    args = {'tool_conditions':tool_conditions,'request_id':requestId}
    print (errors)
    if errors is not None:
        args['errors']= errors
    args.update(csrf(request))
    return render(request, 'ToolShare/ack-return.html', args, context_instance=RequestContext(request))










