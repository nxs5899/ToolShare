from ToolShare.models import Tool, Registrant, BorrowTool, ShareZone, Shed, Notification, ToolStatus
from ToolShare.forms import BorrowToolForm, ReturnToolForm, UpdateShedForm
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404



def update_shed(request, shedid):
    '''
    1. Get the shed object based on the id
    2. Get the list of shed coordinators
    '''

    shed_object = get_object_or_404(Shed, pk=shedid)
    user = get_object_or_404(Registrant, pk=request.user.pk)
    shed_coordinators = shed_object.get_shed_coordinators()
    #shed_coordinators = Registrant.objects.filter(role='SHD')
    #shed_coordinators = shed_coordinators.filter(sharezone=user.sharezone)
    all_shed_users = Registrant.objects.filter(sharezone=shed_object.sharezone).exclude(role='SHD')

    form = UpdateShedForm(instance=shed_object)
    args={'shed':shed_object,'shed_coordinators':shed_coordinators,'form':form, 'all_shed_users':all_shed_users}

    if request.POST:
        form = UpdateShedForm(request.POST,instance=shed_object)
        if form.is_valid():
            shed = form.save(commit=False)
            #shed.shed_coordinators = request.shed_coordinators
            shed.save()


            '''The new shed coordinaotrs sent from the UI'''
            newSC = request.POST.get('newSC').split(';')

            '''Remove the users who are no longer Shed Coordinators'''
            for shed_coordinator in shed_coordinators:
                if not str(shed_coordinator.pk) in newSC:
                    '''change the role of the user'''
                    shed_coordinator.role = 'BAS'
                    shed_coordinator.save()


            '''Add the users who are new Shed Coordinators'''

            oldSC = [];
            for shed_coordinator in shed_coordinators:
                    oldSC.append(str(shed_coordinator.pk))

            for userID in newSC:
                if not userID == '':
                    if not userID in oldSC:
                        user = get_object_or_404(Registrant, pk=userID)
                        user.role = 'SHD'
                        user.save()

                        # shedCordinator = ShedCoordinator.objects.create()
                        # shedCordinator.shed = shed_object
                        # shedCordinator.user = get_object_or_404(Registrant, pk=userID)
                        # shedCordinator.save()
                        #
                        # shedCordinator.user.role = 'SHD'
                        # shedCordinator.user.save()



            return HttpResponseRedirect('/ToolShare/shed-tools/')
        else:
            form_errors = form.errors
            print(form_errors)

    return render(request, 'ToolShare/shed-update.html', args, context_instance=RequestContext(request))