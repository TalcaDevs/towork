from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Formulario para crear un nuevo usuario desde el backoffice"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'rol', 'foto_perfil', 
                 'descripcion', 'telefono', 'ubicacion', 'linkedin', 'id_portafolio_web']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Aplicar clases a los campos para mantener coherencia con los estilos
        for field_name, field in self.fields.items():
            if field_name not in ['is_active']:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Etiquetas en español
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'
        
        # Placeholders
        self.fields['email'].widget.attrs.update({'placeholder': 'ejemplo@towork.com'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Ingrese el nombre'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Ingrese el apellido'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Ingrese la contraseña'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirme la contraseña'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username', email)  # Si no hay username, usar email
        
        # Si no es una edición o es un usuario diferente
        if not self.instance.pk or self.instance.email != email:
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("Ya existe un usuario con este email.")
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Usar email como nombre de usuario
        if commit:
            user.save()
        return user


class CustomUserEditForm(forms.ModelForm):
    """Formulario para editar un usuario existente desde el backoffice"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'rol', 'is_active', 'foto_perfil', 
                 'descripcion', 'telefono', 'ubicacion', 'linkedin', 'id_portafolio_web']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        
        # Aplicar clases a los campos para mantener coherencia con los estilos
        for field_name, field in self.fields.items():
            if field_name not in ['is_active']:
                field.widget.attrs.update({'class': 'form-control'})
                
        # Etiquetas en español
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['email'].label = 'Email'
        self.fields['foto_perfil'].label = 'URL de Foto de Perfil'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['telefono'].label = 'Teléfono'
        self.fields['ubicacion'].label = 'Ubicación'
        self.fields['linkedin'].label = 'LinkedIn'
        self.fields['id_portafolio_web'].label = 'Portafolio Web'
        
        # Placeholders
        self.fields['email'].widget.attrs.update({'placeholder': 'ejemplo@towork.com'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Ingrese el nombre'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Ingrese el apellido'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Si es una edición y el email ha cambiado
        if self.instance.pk and self.instance.email != email:
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError("Ya existe un usuario con este email.")
        
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Usar email como nombre de usuario
        if commit:
            user.save()
        return user