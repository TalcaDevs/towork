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
        
        # Si ya existe un usuario con ese email, no dejar crear otro
        self.fields['email'].widget.attrs.update({'placeholder': 'ejemplo@towork.com'})
    
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