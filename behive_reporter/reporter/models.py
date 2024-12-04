from django.db import models
from PIL import Image
import uuid
import os
from PIL.ExifTags import TAGS
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password  # Importar métodos para segurança de senhas
from django.core.exceptions import ValidationError  # Importar ValidationError para validação de email

class Tecnico(models.Model):
    idtecnico = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    def clean(self):
        if Tecnico.objects.filter(email=self.email).exists():
            raise ValidationError("Email já está em uso.")

    def __str__(self):
        return self.nome


class Sitio(models.Model):
    idsitio = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    CEP = models.CharField(max_length=8)
    cidade = models.CharField(max_length=45)
    endereco = models.CharField(max_length=45)

    def __str__(self):
        return self.nome


class Foto(models.Model):
    idfoto = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='fotos/')
    caminho = models.CharField(max_length=255, blank=True, editable=False)  # Caminho da imagem
    nome = models.CharField(max_length=45, blank=True)
    descricao = models.TextField()  # Manter como TextField para descrições mais longas
    metadados = models.JSONField(null=True, blank=True, editable=False)  # Metadados da imagem
    idsitio = models.ForeignKey(Sitio, on_delete=models.CASCADE)

    def __str__(self):
        return self.descricao
    
    def save(self, *args, **kwargs):
        if self.foto:
            # Renomeia a imagem com base no nome fornecido
            if self.nome:
                # Obtém a extensão do arquivo original
                ext = os.path.splitext(self.foto.name)[1]
                # Define o novo nome do arquivo sem criar diretórios extras
                novo_nome = f"{self.nome}{ext}"

                # Atualiza o caminho para refletir o novo nome sem a criação de pasta extra
                self.foto.name = os.path.join('', novo_nome)
                self.caminho = novo_nome

            # Extrai metadados da imagem
            try:
                image = Image.open(self.foto)
                exif_data = image._getexif()
                self.metadados = {TAGS.get(tag, tag): value for tag, value in exif_data.items()} if exif_data else {}
            except Exception as e:
                print(f"Erro ao extrair metadados: {e}")
                self.metadados = {}  # Caso de erro, define como vazio

        super().save(*args, **kwargs)

class Administrador(models.Model):
    idadministrador = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    senha = models.CharField(max_length=128)  # Aumentado para 128 para suportar hash de senha

    def save(self, *args, **kwargs):
        """Hash the password before saving the Admin instance."""
        if self.senha:
            self.senha = make_password(self.senha)  # Hash a senha
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """Check the hashed password."""
        return check_password(raw_password, self.senha)

    def __str__(self):
        return self.nome


class Empresa(models.Model):
    idempresa = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)

    def __str__(self):
        return self.nome


def default_pedidos_fotos():
    return [{"descricao": "Foto 1"}, {"descricao": "Foto 2"}]

class TemplateRelatorio(models.Model):
    idtemplate_relatorio = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45, default="")  # Nome do template
    pedidos_fotos = models.JSONField(
        default=default_pedidos_fotos,
        help_text="Especifique as fotos que precisam ser solicitadas para este relatório em formato JSON."
    )
    administrador = models.ForeignKey(Administrador, on_delete=models.CASCADE)
    idempresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"Template: {self.nome} (ID: {self.idtemplate_relatorio})"


class RelatorioFinal(models.Model):
    idrelatorio_final = models.AutoField(primary_key=True) #
    nome= models.CharField(max_length=45) #
    endereco_server = models.CharField(max_length=150, blank=True, null=True, editable=False)
    tecnico_responsavel = models.ForeignKey('Tecnico', on_delete=models.CASCADE) #
    idsitio = models.ForeignKey('Sitio', on_delete=models.CASCADE) #
    idtemplate_relatorio = models.ForeignKey('TemplateRelatorio', on_delete=models.CASCADE) #
    data = models.DateField() #
    fotos = models.ManyToManyField('Foto') #
    data_visita = models.DateField() 
    created_at = models.DateTimeField(auto_now_add=True) #
    updated_at = models.DateTimeField(auto_now=True) #

    def save(self, *args, **kwargs):
        if not self.endereco_server:
            self.endereco_server = "relatorios/"  # substitua pelo endereço desejado
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report from {self.data} - {self.idsitio.nome}"
