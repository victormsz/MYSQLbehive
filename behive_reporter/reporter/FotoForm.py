from django import forms
from .models import Foto, RelatorioFinal

class FotoForm(forms.ModelForm):
    class Meta:
        model = Foto
        fields = ['foto', 'nome', 'descricao', 'idsitio']  # Inclua os campos necessários

class RelatorioForm(forms.ModelForm):
    class Meta:
        model = RelatorioFinal
        fields = ['nome', 'idtemplate_relatorio']

    # Se você precisar de alguma validação extra ou customização, pode adicionar aqui
    def clean_nome(self):
        nome = self.cleaned_data.get('nome')
        if len(nome) < 3:
            raise forms.ValidationError("O nome do relatório deve ter pelo menos 3 caracteres.")
        return nome