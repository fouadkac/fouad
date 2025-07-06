from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import License, Robot

# Vue personnalisée pour lister les licences
@staff_member_required
def list_licenses_view(request):
    licenses = License.objects.all()
    context = {
        'licenses': licenses,
        'title': 'Liste des Licences'
    }
    return render(request, "admin/license_list.html", context)

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("owner", "login_id", "broker", "license_type", "active")
    search_fields = ("owner__username", "broker", "login_id")
    list_filter = ("license_type", "active")

@admin.register(Robot)
class RobotAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class MyAdminSite(admin.AdminSite):
    site_header = "Administration Pilot Fish"
    site_title = "Pilot Fish Admin"
    index_title = "Tableau de bord Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-dashboard/', self.admin_view(self.custom_dashboard_view), name="custom-dashboard"),
            path('license-list/', self.admin_view(list_licenses_view), name="license-list"),
        ]
        return custom_urls + urls

    def custom_dashboard_view(self, request):
        context = dict(
            self.each_context(request),
            robots_count=Robot.objects.count(),
            licenses_count=License.objects.count(),
        )
        return TemplateResponse(request, "admin/custom_dashboard.html", context)

admin_site = MyAdminSite(name='myadmin')
admin_site.register(License, LicenseAdmin)
admin_site.register(Robot, RobotAdmin)
