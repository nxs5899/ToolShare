from django.db import models
from django.core.validators import RegexValidator
from django import forms
from django.forms import ModelForm
from datetime import date
from html import unescape

from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from html.parser import HTMLParser
import html

class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password,
                      is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email).lower()
        # zipcode = extra_fields.zipcode
        #  if not zipcode:
          #  raise ValueError('A zipcode is required')

        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class ToolStatus(models.Model):
    status_code = models.CharField(max_length=2, unique=True, verbose_name=u"Status Code")
    status_name = models.CharField(max_length=15, verbose_name=u"Status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.status_name


class ToolCondition(models.Model):
    condition_code = models.CharField(max_length=2, unique=True, verbose_name=u"Condition Code")
    condition_name = models.CharField(max_length=30, verbose_name=u"Condition")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.condition_name


class ToolLocation(models.Model):
    location_code = models.CharField(max_length=2, unique=True, verbose_name=u"Location Code")
    location_name = models.CharField(max_length=15, verbose_name=u"Location")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.location_name


class ToolCategory(models.Model):
    category_code = models.CharField(max_length=2, unique=True, verbose_name=u"Category Code")
    category_name = models.CharField(max_length=30, verbose_name=u"Category")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name


class ShareZone(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    zip_code = models.CharField(max_length=6, blank=False)
    #registrants = models.OneToManyField(Registrant)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class Registrant(AbstractBaseUser, PermissionsMixin):
    BAS = 'BAS'
    SHD = 'SHD'
    SYS = 'SYS'
    ROLE_CHOICES = (
        (BAS, "Basic User"),
        (SHD, "Shed Coordinator"),
        (SYS, "System Administrator")
    )
    APPROVAL_CHOICES = (
        ('Pending', "Pending"),
        ('Approved', "Approved"),
        ('Rejected', "Rejected")
    )

    phone_regex = RegexValidator(regex=r'^(1?(-?\d{3})-?)?(\d{3})(-?\d{4})$',message="Phone number must be between 7- 10 digits.")
    password_regex = RegexValidator(regex=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,50}$', message="Password must have at least 8 characters and must include at least one upper case letter, one lower case letter, and one numeric digit.")

    email = models.EmailField(unique=True, blank=False)
    #password = models.CharField(validators=[password_regex], blank=False, max_length=50)

    first_name = models.CharField(max_length=225, blank=False)
    last_name = models.CharField(max_length=225, blank=False)
    date_of_birth = models.DateField(blank=True, null=True)

    address_line1 = models.CharField(max_length=225, blank=False)
    address_line2 = models.CharField(max_length=225, blank=True)
    telephone = models.CharField(validators=[phone_regex], blank=False, max_length=10)

    approval_status = models.CharField(max_length=225, choices=APPROVAL_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, default=BAS)
    sharezone = models.ForeignKey(ShareZone, on_delete=models.CASCADE, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.first_name + ' ' + self.last_name


    verbose_name = _('user')
    verbose_name_plural = _('users')

    def get_absolute_url(self):
            return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
            """
            Returns the first_name plus the last_name, with a space in between.
            """
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

    def get_short_name(self):
            "Returns the short name for the user."
            return self.first_name

    def email_user(self, subject, message, from_email=None):
            """
            Sends an email to this User.
            """
            send_mail(subject, message, from_email, [self.email])

    def get_zip_code(self):
        return self.sharezone.zip_code

    def get_shed(self):
        return Shed.objects.get(sharezone=self.sharezone)

    def filter_by_zip_code(zip_code):
        share_zone = ShareZone.objects.get(zip_code=zip_code)
        users = Registrant.objects.filter(sharezone=share_zone)
        return users

    def is_currently_borrowing_tools(self):
        borrowing_tools = BorrowTool.objects.filter(currently_borrowed = True).filter(borrowerId = self)
        if borrowing_tools.count() >= 1:
            return True
        else:
            return False

    def has_all_tools_available(self):
        status = ToolStatus.objects.get(status_code = 'BR')
        borrowed_tools = Tool.objects.filter(tool_owner=self).filter(tool_status = status)
        if borrowed_tools.count() >= 1:
            return True
        else:
            return False

    def delete_user(self):
        # proceed with the soft delete only if the user is currently (not lending) and (not borrowing) a tool
        if (not self.has_all_tools_available()) & (not self.is_currently_borrowing_tools()):
            # deactivate the user
            self.is_deleted = True
            self.approval_status = 'Pending'
            self.save()
            owned_tools = Tool.objects.filter(tool_owner=self)
            # deactivate all tools the user owns
            for tool in owned_tools:
                tool.delete_tool()
            return True
        else:
            # cannot delete the user
            return False

    def restore_user(self):
        if self.is_deleted:
            self.is_deleted = False
            self.approval_status = 'Approved'
            self.save()
            owned_tools = Tool.objects.filter(tool_owner=self)
            for tool in owned_tools:
                tool.restore_tool()
            return True
        else:
            return False

    def has_unread_notifications(self):
        notifications = Notification.objects.filter(recipient=self).filter(viewed=False)
        if notifications.count() >= 1:
            return True
        else:
            return False


class Shed(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    #shed_coordinators = models.One(Registrant)
    #tools = models.OneToManyField(To
    #zip_code = models.CharField(max_length=6,blank=False, default='14623')
    sharezone = models.ForeignKey(ShareZone,on_delete = models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_shed_coordinators(self):
        return Registrant.objects.filter(sharezone=self.sharezone).filter(role='SHD').filter(is_deleted=False)

    def add_shed_coordinator(self, user_id):
        user = Registrant.objects.filter(pk=user_id)
        user.role = 'SHD'
        user.edited = 1
        user.save()

    def remove_shed_coordinator(self, user_id):
        user = Registrant.objects.filter(pk=user_id)
        user.role = 'BAS'
        user.edited = 1
        user.save()

    def get_shed_tools(self):
        home_location = ToolLocation.objects.get(location_name='Home')
        users = Registrant.objects.filter(sharezone=self.sharezone)
        tools = []
        for user in users:
            user_tools = Tool.objects.filter(tool_owner=user).exclude(tool_location=home_location)
            for tool in user_tools:
                tools.append(tool)

        return tools



# class ShedCoordinator(models.Model):
#     user = models.ForeignKey(Registrant, on_delete=models.CASCADE, blank=True,null=True)
#     shed = models.ForeignKey(Shed, on_delete=models.CASCADE,blank=True,null=True)
#
#     def __str__(self):
#         return self.shed.name


class Tool(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    instructions = models.TextField(blank=True,null=True)
    tool_category = models.ForeignKey(ToolCategory, on_delete=models.CASCADE)
    tool_condition = models.ForeignKey(ToolCondition, on_delete=models.CASCADE)
    tool_location = models.ForeignKey(ToolLocation, on_delete=models.CASCADE)
    tool_status = models.ForeignKey(ToolStatus, on_delete=models.CASCADE)
    tool_owner = models.ForeignKey(Registrant, on_delete=models.CASCADE)
    #shed = models.ForeignKey(Shed, on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    def getCategory(self):
        return self.category
    def getToolLocation(self):
        return self.tool_location


    def get_shed(self):
        user = Registrant.objects.get(pk=self.tool_owner.pk)
        share_zone = ShareZone.objects.get(pk=user.sharezone.pk)
        shed = Shed.objects.get(pk=share_zone.pk)

        return shed

    def filter_by_zip_code(zip_code):
        share_zone = ShareZone.objects.get(zip_code=zip_code)
        users = Registrant.objects.filter(sharezone=share_zone).filter(is_deleted = False)
        tools = []
        for user in users:
            user_tools = Tool.objects.filter(tool_owner=user).filter(is_deleted = False)
            for tool in user_tools:
                tools.append(tool)
        return tools

    def filter_deleted_tools_by_zip_code(zip_code):
        share_zone = ShareZone.objects.get(zip_code=zip_code)
        users = Registrant.objects.filter(sharezone=share_zone)
        tools = []
        for user in users:
            user_tools = Tool.objects.filter(tool_owner=user).filter(is_deleted = True)
            for tool in user_tools:
                tools.append(tool)
        return tools

    def delete_tool(self):
        '''
           Perform a soft delete
           Rules that prevent deletion
           1. Tool should not be in the Borrowed State
           2. Tool should not be in the Blackout/Deactivated State
           i.e. tool must have the status Available
        '''
        if self.tool_status.status_name != 'Borrowed':
            deleted_status = ToolStatus.objects.get(status_name='Deactivated')
            self.is_deleted = True
            self.tool_status = deleted_status
            self.save()
            return True
        else:
            return False

    def restore_tool2(self):
        '''
           Restore (UnDelete) a tool
        '''
        if self.tool_status.status_name == 'Deactivated' and self.is_deleted == True:
            available_status = ToolStatus.objects.get(status_name='Available')
            self.is_deleted = False
            self.tool_status = available_status
            self.save()

            if self.tool_owner.is_deleted == True:
                self.tool_owner.is_deleted = False
                self.tool_owner.save()

            return True
        else:
            return False

    def restore_tool(self):
        '''
           Restore (UnDelete) a tool
        '''
        if self.tool_status.status_name == 'Deactivated' and self.is_deleted == True:
            available_status = ToolStatus.objects.get(status_name='Available')
            self.is_deleted = False
            self.tool_status = available_status
            self.save()
            return True
        else:
            return False

#how to add a notification
#notification.sendNotification(a_notification_type_from those_in the mapper, optional_arguments_in_a_dict)
class Notification(models.Model):
    title = models.CharField(max_length=500, verbose_name=u"Title")
    message = models.TextField(verbose_name=u"Message")
    viewed = models.BooleanField(default=False, verbose_name=u"Viewd?")
    recipient = models.ManyToManyField(Registrant)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title + '' + self.message

    notification_message_mapper = {
        "Borrow_Request": "There is a new request for the tool toolId. Please approve or reject the request from the ",
        "Borrow_Request_Confirmed": "Your request for toolId has been approved",
        "Borrow_Request_Rejected": "Your request for toolId has been rejected",
        "Acknowledge_tool_return": "toolId has been returned. Please update the status and condition of the tool",
        "Tool_Blackout": "toolId has been made unavailable until X date. Please request to borrow the same for after this period",
        "Tool_Damaged": "toolId has been made unavailable until further notice",
        "Tool_Deactivated": "toolId has been made unavailable until further notice",
        "Borrow_Shed": "toolId has been borrowed by borrowerId",
        "User_Approval":"userId has registered on ToolShare. Please approve the join request from the ",
        "Tool_Returned_Home":"Your tool toolId has been returned by userId. Please acknowledge this return and specify the tool's condition ",
        "Tool_Returned_Shed":"The tool toolId has been returned to the shed by userId. Please acknowledge this return and specify the tool's condition ",
        "User_Approval":"userId has registered on ToolShare. Please approve the join request from the ",
        "Update_Shed": "userId Please update your Shed address from the ",
    }

    def get_display_title(self):
        if self.title == 'Borrow_Request':
            return 'New Borrow Request'
        if self.title == 'Borrow_Request_Confirmed':
            return 'Borrow Request Confirmed'
        if self.title == 'Borrow_Request_Rejected':
            return 'Borrow Request Rejected'
        if self.title == 'Acknowledge_tool_return':
            return 'Acknowledge Returned Tool'
        if self.title == 'Tool_Blackout':
            return 'Tool Blackout'
        if self.title == 'Tool_Damaged':
            return 'Tool Damaged'
        if self.title == 'Tool_Deactivated':
            return 'Tool Deactivated'
        if self.title == 'User_Approval':
            return 'New User Approval'
        if self.title == 'Tool_Returned_Home':
            return 'Tool Returned'
        if self.title == 'Tool_Returned_Shed':
            return 'Tool Returned to Shed'
        if self.title == 'Update_Shed':
            return 'Update Shed'
        if self.title == 'Borrow_Shed':
            return 'Tool Borrowed from Shed'


    def _constructNotificationMessage(self, type, message, args=None):
        custom_message = ""
        if 'toolid' in args:
            tool = Tool.objects.get(pk=args['toolid'])
            custom_message = message.replace('toolId', tool.name)
        if 'toolid' in args and 'borrowerid' in args:
            user = Registrant.objects.get(pk=args['borrowerid'])
            tool = Tool.objects.get(pk=args['toolid'])
            custom_message = message.replace('toolId', tool.name)
            custom_message = custom_message.replace('borrowerId', user.first_name + " " + user.last_name + " (" + user.email + ")")
        if type == 'User_Approval':
            user = Registrant.objects.get(pk=args['userid'])
            custom_message = message.replace('userId', user.first_name + " " + user.last_name + " (" + user.email + ")")
            goto = "http://127.0.0.1:8000/ToolShare/admin/manage-users/"
            custom_message = custom_message + unescape("<a href='" + goto + "'>Manage Users Page</a>")
        if type == 'Update_Shed':
            user = Registrant.objects.get(pk=args['userid'])
            custom_message = message.replace('userId', '')
            shed = user.get_shed()
            goto = "/ToolShare/shed/shed-update/"+str(shed.pk)+"/"
            custom_message = custom_message + unescape("<a href='" + goto + "'>Update Shed Page</a>")
        if type == 'Borrow_Request':
            goto = "http://127.0.0.1:8000/ToolShare/request/" + args['borrow_request']
            custom_message = custom_message + unescape("<a href='" + goto +"'>Requests Page</a>")
        if type == 'Tool_Returned_Home' or type == 'Tool_Returned_Shed':
            user = Registrant.objects.get(pk=args['userid'])
            custom_message = custom_message.replace('userId', user.first_name + " " + user.last_name + " (" + user.email + ")")
            goto = "http://127.0.0.1:8000/ToolShare/ack-return/"+args['borrow_request']
            custom_message = custom_message + unescape("<a href='" + goto + "'>here</a>")

        return custom_message

    def sendNotification(self, type, recipients, args=None):
        notification = self
        notification.title = type
        notification.message = self._constructNotificationMessage(type, self.notification_message_mapper[type], args)
        print("constructed message " + notification.message)
        notification.save()
        notification.recipient.set(recipients)
        notification.save()


class BorrowTool(models.Model):
    toolId = models.ForeignKey(Tool, on_delete=models.CASCADE)
    borrowerId = models.ForeignKey(Registrant, on_delete=models.CASCADE)
    borrower_notes = models.TextField(blank=True,null=True)
    lender_notes = models.TextField(blank=True,null=True)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    currently_borrowed = models.BooleanField(default=False)
    return_date = models.DateField(blank=True, null=True)
    return_condition = models.ForeignKey(ToolCondition, on_delete=models.CASCADE, null=True, blank=True)
    return_acknowledgement = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


    def __str__(self):
        return str(self.toolId)


    def currently_borrowed_by_zip(zipcode):
        tools = Tool.filter_by_zip_code(zipcode)
        borrowed_tools = []
        for tool in tools:
            borrowed_tool = BorrowTool.objects.filter(toolId=tool.pk, currently_borrowed=True)
            if borrowed_tool.count() != 0:
                borrowed_tools.append(borrowed_tool[0])

        return borrowed_tools

    # def filter_by_zip_code(zip_code):
    #     share_zone = ShareZone.objects.get(zip_code=zip_code)
    #     users = Registrant.objects.filter(sharezone=share_zone)
    #     borrows = []
    #     for user in users:
    #         borrow_tools = BorrowTool.objects.filter(borrowerId=user)
    #         for borrowers in borrow_tools:
    #             borrows.append(borrowers)
    #
    #     return borrows


class ReturnTool(models.Model):
    toolId = models.ForeignKey(Tool, on_delete=models.CASCADE)
    borrowerId = models.ForeignKey(BorrowTool, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.toolId)


class BlackoutTool(models.Model):
    toolId = models.ForeignKey(Tool, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    end_date = models.DateField(auto_now=False, auto_now_add=False)
    is_deleted = models.BooleanField(default=False)