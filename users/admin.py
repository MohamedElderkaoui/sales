# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import RevUser


@admin.register(RevUser)
class RevUserAdmin(BaseUserAdmin):
    """Administrador personalizado para usuarios extendidos"""
    
    # Campos a mostrar en la lista
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'get_role_badge',
        'phone',
        'is_active',
        'get_status',
        'date_joined'
    ]
    
    list_filter = [
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
    ]
    
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'phone'
    ]
    
    ordering = ['-date_joined']
    
    # Campos editables directamente en la lista
    list_editable = []
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Rol y Permisos', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Campos para crear nuevo usuario
    add_fieldsets = (
        ('Credenciales', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Rol', {
            'fields': ('role',)
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']
    
    date_hierarchy = 'date_joined'
    
    actions = [
        'make_admin',
        'make_analyst',
        'make_manager',
        'activate_users',
        'deactivate_users'
    ]
    
    # Métodos personalizados
    
    @admin.display(description='Rol', ordering='role')
    def get_role_badge(self, obj):
        role_styles = {
            'admin': ('🔑 Admin', 'background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;'),
            'manager': ('👔 Manager', 'background: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-weight: bold;'),
            'analyst': ('📊 Analyst', 'background: #17a2b8; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;'),
        }
        
        label, style = role_styles.get(obj.role, ('Usuario', 'background: gray; color: white; padding: 3px 8px; border-radius: 3px;'))
        return format_html('<span style="{}">{}</span>', style, label)
    
    @admin.display(description='Estado General')
    def get_status(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: purple; font-weight: bold;">⚡ Superusuario</span>')
        elif obj.is_staff:
            return format_html('<span style="color: blue;">🔧 Staff</span>')
        elif obj.is_active:
            return format_html('<span style="color: green;">✓ Activo</span>')
        else:
            return format_html('<span style="color: red;">✗ Inactivo</span>')
    
    # Acciones personalizadas
    
    @admin.action(description='Cambiar rol a Admin')
    def make_admin(self, request, queryset):
        updated = queryset.update(role='admin')
        self.message_user(
            request,
            f'{updated} usuario(s) cambiado(s) a rol Admin.'
        )
    
    @admin.action(description='Cambiar rol a Analyst')
    def make_analyst(self, request, queryset):
        updated = queryset.update(role='analyst')
        self.message_user(
            request,
            f'{updated} usuario(s) cambiado(s) a rol Analyst.'
        )
    
    @admin.action(description='Cambiar rol a Manager')
    def make_manager(self, request, queryset):
        updated = queryset.update(role='manager')
        self.message_user(
            request,
            f'{updated} usuario(s) cambiado(s) a rol Manager.'
        )
    
    @admin.action(description='Activar usuarios')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} usuario(s) activado(s).'
        )
    
    @admin.action(description='Desactivar usuarios')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} usuario(s) desactivado(s).'
        )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Agregar anotaciones si es necesario
        return qs
    
    def save_model(self, request, obj, form, change):
        """Lógica personalizada al guardar"""
        super().save_model(request, obj, form, change)
        
        if change:
            self.message_user(
                request,
                f'Usuario "{obj.username}" actualizado correctamente.'
            )
        else:
            self.message_user(
                request,
                f'Usuario "{obj.username}" creado exitosamente con rol {obj.get_role_display()}.'
            )
