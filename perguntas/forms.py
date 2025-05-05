from django import forms
from .models import Enquete, Aluno, Opcao

class RespostaForm(forms.Form):
    def __init__(self, perguntas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for pergunta in perguntas:
            if pergunta.tipo == 'unica':
                self.fields[f'pergunta_{pergunta.id}'] = forms.ModelChoiceField(
                    queryset=Opcao.objects.filter(pergunta=pergunta),
                    widget=forms.RadioSelect(),
                    label=pergunta.texto,
                    required=pergunta.obrigatoria
                )
            elif pergunta.tipo == 'multipla':
                self.fields[f'pergunta_{pergunta.id}'] = forms.ModelMultipleChoiceField(
                    queryset=Opcao.objects.filter(pergunta=pergunta),
                    widget=forms.CheckboxSelectMultiple(),
                    label=pergunta.texto,
                    required=pergunta.obrigatoria
                )
            elif pergunta.tipo == 'texto':
                self.fields[f'pergunta_{pergunta.id}'] = forms.CharField(
                    widget=forms.Textarea,
                    label=pergunta.texto,
                    required=pergunta.obrigatoria
                )

class CriarEnqueteForm(forms.ModelForm):
    class Meta:
        model = Enquete
        fields = ['titulo', 'descricao', 'data_encerramento', 'ativa']
        widgets = {
            'data_encerramento': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class RegistrarAlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['nome', 'email', 'nivel_programacao', 'linguagem_favorita']

class FiltrarEnquetesForm(forms.Form):
    titulo = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'placeholder': 'Filtrar por título'}))
    status = forms.ChoiceField(choices=[('', 'Todos'), ('ativa', 'Ativas'), ('encerrada', 'Encerradas')], required=False, widget=forms.Select)