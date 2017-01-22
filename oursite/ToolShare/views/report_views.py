from ToolShare.models import Tool, Registrant, ShareZone, Shed, ToolLocation, ToolCategory, ToolCondition, ToolStatus, BorrowTool
from ToolShare.forms import AdminCreateForm
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.db.models import Count
from django.shortcuts import render, get_object_or_404


def most_active_borrowers(request):
    if request.user.role == 'SYS':
        zones = ShareZone.objects.all()
        if request.POST:
            zone_id = request.POST.get('zone_id')
        else:
            zone_id = zones[0].pk

        sharezone = get_object_or_404(ShareZone, pk=zone_id)
        borrowers = Registrant.objects.filter(sharezone=sharezone).filter(approval_status='Approved').distinct()  #BorrowTool.objects.values_list('borrowerId', flat=True).distinct()
        borrowtool = {}

        for distincts in borrowers:
            count = BorrowTool.objects.filter(borrowerId=distincts).count()
            userobj = get_object_or_404(Registrant,pk=distincts.pk)
            if userobj.sharezone == sharezone:
                borrowtool[userobj] = count

        args = {'zones': zones, 'borrowers': borrowtool, 'currentzone': sharezone}
        return render(request, 'ToolShare/report-active-borrowers.html', args)

    else:
        zone = request.user.sharezone
        borrowers = Registrant.objects.filter(sharezone=zone).filter(approval_status='Approved').distinct() #BorrowTool.objects.values_list('borrowerId', flat=True).distinct()
        borrowtool = {}
        for distincts in borrowers:
            count = BorrowTool.objects.filter(borrowerId=distincts).count()
            userobj = get_object_or_404(Registrant,pk=distincts.pk)
            if userobj.sharezone == zone:
                borrowtool[userobj] = count

        args = {'borrowers': borrowtool,'currentzone': zone}

        return render(request, 'ToolShare/report-active-borrowers.html', args)


def most_active_lenders(request):
    if request.user.role == 'SYS':
        zones = ShareZone.objects.all()
        if request.POST:
            zone_id = request.POST.get('zone_id')
        else:
            zone_id = zones[0].pk

        sharezone = get_object_or_404(ShareZone, pk=zone_id)
        disLender = Registrant.objects.filter(sharezone=sharezone).filter(approval_status='Approved').distinct() #Tool.objects.values_list('tool_owner', flat=True).distinct()
        lenders = {}
        for distincts in disLender:
            count = BorrowTool.objects.filter(toolId__tool_owner = distincts).count()
            userobj = get_object_or_404(Registrant,pk=distincts.pk)
            if userobj.sharezone == sharezone:
                lenders[userobj] = count

        args = {'lenders': lenders, 'zones':zones,'currentzone': sharezone}
        return render(request, 'ToolShare/report-active-lenders.html', args)

    else:
        zone = request.user.sharezone
        disLender = Registrant.objects.filter(sharezone=zone).filter(approval_status='Approved').distinct() #Tool.objects.values_list('tool_owner', flat=True).distinct()
        lenders = {}

        for distincts in disLender:
            count = BorrowTool.objects.filter(toolId__tool_owner = distincts).count()
            userobj = get_object_or_404(Registrant,pk=distincts.pk)
            if userobj.sharezone == zone:
                lenders[userobj] = count

        args = {'lenders': lenders,'currentzone': zone}
        return render(request, 'ToolShare/report-active-lenders.html', args)


def most_borrowed_tools(request):
    if request.user.role == 'SYS':
        zones = ShareZone.objects.all()
        if request.POST:
            zip_code = request.POST.get('zip_code')
        else:
            zip_code = zones[0].zip_code

        sharezone = get_object_or_404(ShareZone, zip_code=zip_code)
        distools = Tool.filter_by_zip_code(zip_code)
        tools = {}

        for distincts in distools:
            # print(distincts)
            count = BorrowTool.objects.filter(toolId = distincts.pk).count()
            toolobj = get_object_or_404(Tool, pk=distincts.pk)
            # objshed = toolobj.get_shed()
            # if toolobj.get_shed() == shed:
            tools[toolobj] = count

        args = {'tools': tools, 'zones':zones, 'currentzone': sharezone}
        return render(request, 'ToolShare/report-most-tools.html', args)

    else:
        zip_code  = request.user.get_zip_code()
        disTool = Tool.filter_by_zip_code(zip_code)

        # shed = request.user.get_shed()
        # disTool = BorrowTool.objects.values_list('toolId', flat=True).distinct()
        tools = {}

        for distincts in disTool:

            count = BorrowTool.objects.filter(toolId = distincts.pk).count()
            toolobj = get_object_or_404(Tool, pk=distincts.pk)

            # shed_tool = toolobj.get_shed
            # if shed_tool.pk == shed.pk:
            tools[toolobj] = count

        args = {'tools': tools, 'currentzone': request.user.sharezone}
        return render(request, 'ToolShare/report-most-tools.html', args)


def recent_tools(request):
    if request.user.role == 'SYS':
        zones = ShareZone.objects.all()
        if request.POST:
            zip_code = request.POST.get('zip_code')
        else:
            zip_code = zones[0].zip_code

        sharezone = get_object_or_404(ShareZone, zip_code=zip_code)
        borrowtools = BorrowTool.currently_borrowed_by_zip(zip_code)

        args = {'borrowtools': borrowtools, 'currentzone':sharezone, 'zones':zones}
        return render(request, 'ToolShare/report-recent-tools.html', args)

    else:
        zip = request.user.get_zip_code()
        borrowtools = BorrowTool.currently_borrowed_by_zip(zip)

        args = {'borrowtools': borrowtools,'currentzone': request.user.sharezone}
        return render(request, 'ToolShare/report-recent-tools.html', args)


def tool_history(request):
    if request.user.role == 'SYS':
        sharezones = ShareZone.objects.all()

        if request.POST:
            zone_id = request.POST.get('zone_id')
            zoneObject = ShareZone.objects.get(pk=zone_id)
            tools = Tool.filter_by_zip_code(zoneObject.zip_code)

            tool_id = request.POST.get('tool_id')
            tool_temp = Tool.objects.filter(pk=int(tool_id))
            if tool_temp.count() == 0:
                tool_id = tools[0].pk
        else:
            zoneObject = sharezones[0]
            tools = Tool.filter_by_zip_code(zoneObject.zip_code)
            tool_id = tools[0].pk
            zone_id = zoneObject.pk

        toolObject = get_object_or_404(Tool, pk=tool_id)
        tool_hist = BorrowTool.objects.filter(toolId=tool_id)

        args = {'sharezones':sharezones,'tools': tools, 'toolObject': toolObject, 'tool_hist': tool_hist, 'selectedTool': int(tool_id), 'selectedZone': int(zone_id)}
        return render(request, 'ToolShare/report-tool-history.html', args)

    else:
        zip = request.user.get_zip_code()
        # tools = Tool.filter_by_zip_code(zip)
        if request.POST:
            tools = Tool.filter_by_zip_code(zip)
            tool_id = request.POST.get('tool_id')
            tool_temp = Tool.objects.filter(pk=int(tool_id))
            if tool_temp.count() == 0:
                tool_id = tools[0].pk
        else:
            tools = Tool.filter_by_zip_code(zip)
            tool_id = tools[0].pk
        toolObject = get_object_or_404(Tool, pk=tool_id)
        tool_hist = BorrowTool.objects.filter(toolId=tool_id)
        args = {'tools': tools, 'toolObject': toolObject, 'tool_hist': tool_hist, 'selectedTool': int(tool_id)}
        return render(request, 'ToolShare/report-tool-history.html', args)


def user_history(request):
    if request.user.role == 'SYS':
        sharezones = ShareZone.objects.all()

        if request.POST:
            zone_id = request.POST.get('zone_id')
            people = Registrant.objects.filter(sharezone__pk=zone_id).filter(approval_status='Approved')

            user_id = request.POST.get('user_id')
            user_temp = Registrant.objects.filter(pk=int(user_id)).filter(sharezone__pk=zone_id)
            if user_temp.count() == 0:
                user_id = people[0].pk
        else:
            zone_id = sharezones[0].pk
            people = Registrant.objects.filter(sharezone__pk=zone_id)
            user_id = people[0].pk


        userObject = get_object_or_404(Registrant, pk=user_id)
        user_hist = BorrowTool.objects.filter(borrowerId=user_id)

        args = {'sharezones':sharezones,'people': people, 'userObject': userObject, 'user_hist': user_hist, 'selectedUser': int(user_id), 'selectedZone': int(zone_id)}
        return render(request, 'ToolShare/report-user-history.html', args)

    else:
        sharezones = ShareZone.objects.filter(pk=request.user.sharezone.pk)

        if request.POST:
            people = Registrant.objects.filter(sharezone__pk=request.user.sharezone.pk).filter(approval_status='Approved')
            user_id = request.POST.get('user_id')
        else:
            people = Registrant.objects.filter(sharezone__pk=request.user.sharezone.pk).filter(approval_status='Approved')
            user_id = people[0].pk

        userObject = get_object_or_404(Registrant, pk=user_id)
        user_hist = BorrowTool.objects.filter(borrowerId=user_id)

        args = {'sharezones': sharezones, 'people': people, 'userObject': userObject, 'user_hist': user_hist,
                'selectedUser': int(user_id)}
        return render(request, 'ToolShare/report-user-history.html', args)


