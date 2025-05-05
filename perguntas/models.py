from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

class Enquete(models.Model):
    titulo = models.CharField(_('Título da Enquete'), max_length=200)
    descricao = models.TextField(_('Descrição da Enquete'))
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    data_encerramento = models.DateTimeField(_('Data de Encerramento'), null=True, blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)

    class Meta:
        verbose_name = _('Enquete')
        verbose_name_plural = _('Enquetes')
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo

    @property
    def total_perguntas(self):
        return self.pergunta_set.count()

    @property
    def encerrada(self):
        if self.data_encerramento:
            from django.utils import timezone
            return timezone.now() > self.data_encerramento
        return False

class Pergunta(models.Model):
    enquete = models.ForeignKey(Enquete, verbose_name=_('Enquete'), on_delete=models.CASCADE)
    texto = models.CharField(_('Texto da Pergunta'), max_length=300)
    tipo = models.CharField(
        _('Tipo de Resposta'),
        max_length=20,
        choices=[
            ('unica', _('Única Escolha')),
            ('multipla', _('Múltipla Escolha')),
            ('texto', _('Texto Livre')),
        ]
    )
    obrigatoria = models.BooleanField(_('Obrigatória'), default=True)
    ordem = models.IntegerField(_('Ordem'), default=0)

    class Meta:
        verbose_name = _('Pergunta')
        verbose_name_plural = _('Perguntas')
        ordering = ['ordem']

    def __str__(self):
        return self.texto

    @property
    def total_opcoes(self):
        return self.opcao_set.count()

    @property
    def tem_respostas(self):
        return self.resposta_set.exists()

class Opcao(models.Model):
    pergunta = models.ForeignKey(Pergunta, verbose_name=_('Pergunta'), on_delete=models.CASCADE)
    texto = models.CharField(_('Texto da Opção'), max_length=200)
    valor = models.CharField(_('Valor da Opção'), max_length=50)
    ordem = models.IntegerField(_('Ordem'), default=0)
    slug = models.SlugField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = _('Opção')
        verbose_name_plural = _('Opções')
        ordering = ['ordem']
        unique_together = ('pergunta', 'valor')

    def __str__(self):
        return self.texto

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.texto)
        super().save(*args, **kwargs)

    @property
    def total_respostas(self):
        return self.resposta_set.count()

    @property
    def porcentagem_respostas(self):
        total_geral = self.pergunta.resposta_set.count()
        if total_geral > 0:
            return (self.total_respostas / total_geral) * 100
        return 0

class Aluno(models.Model):
    nome = models.CharField(_('Nome do Aluno'), max_length=150)
    email = models.EmailField(_('Email do Aluno'))
    data_inscricao = models.DateTimeField(_('Data de Inscrição'), auto_now_add=True)
    nivel_programacao = models.CharField(
        _('Nível de Programação'),
        max_length=50,
        choices=[
            ('iniciante', _('Iniciante')),
            ('intermediario', _('Intermediário')),
            ('avancado', _('Avançado')),
        ]
    )
    linguagem_favorita = models.CharField(_('Linguagem Favorita'), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _('Aluno')
        verbose_name_plural = _('Alunos')
        ordering = ['nome']
        unique_together = ('nome', 'email')

    def __str__(self):
        return self.nome

    @property
    def total_respostas(self):
        return self.resposta_set.count()

    @property
    def enquetes_participadas(self):
        return self.resposta_set.values('pergunta__enquete__titulo').distinct().count()

class Resposta(models.Model):
    aluno = models.ForeignKey(Aluno, verbose_name=_('Aluno'), on_delete=models.CASCADE)
    pergunta = models.ForeignKey(Pergunta, verbose_name=_('Pergunta'), on_delete=models.CASCADE)
    data_resposta = models.DateTimeField(_('Data da Resposta'), auto_now_add=True)
    texto_livre = models.TextField(_('Resposta Livre'), blank=True, null=True)
    opcao_unica = models.ForeignKey(Opcao, verbose_name=_('Opção Única'), on_delete=models.SET_NULL, null=True, blank=True, related_name='resposta_unica')

    class Meta:
        verbose_name = _('Resposta')
        verbose_name_plural = _('Respostas')
        ordering = ['-data_resposta']
        unique_together = ('aluno', 'pergunta')

    def __str__(self):
        return f"Resposta de {self.aluno.nome} para {self.pergunta.texto}"

    @property
    def valor_resposta(self):
        if self.opcao_unica:
            return self.opcao_unica.texto
        elif self.texto_livre:
            return self.texto_livre
        return None

    @property
    def enquete(self):
        return self.pergunta.enquete.titulo

class MultiplaEscolhaResposta(models.Model):
    resposta = models.ForeignKey(Resposta, verbose_name=_('Resposta'), on_delete=models.CASCADE)
    opcao = models.ForeignKey(Opcao, verbose_name=_('Opção'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Resposta Múltipla Escolha')
        verbose_name_plural = _('Respostas Múltiplas Escolhas')
        unique_together = ('resposta', 'opcao')

    def __str__(self):
        return f"{self.resposta.aluno.nome} respondeu {self.opcao.texto} em {self.resposta.pergunta.texto}"

    @property
    def texto_opcao(self):
        return self.opcao.texto

    @property
    def pergunta_relacionada(self):
        return self.resposta.pergunta.texto

class AreaInteresse(models.Model):
    nome = models.CharField(_('Nome da Área de Interesse'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    descricao = models.TextField(_('Descrição da Área de Interesse'), blank=True, null=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    ativa = models.BooleanField(_('Ativa'), default=True)

    class Meta:
        verbose_name = _('Área de Interesse')
        verbose_name_plural = _('Áreas de Interesse')
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    ## @property
    ## def total_alunos(self):
    ##    return self.aluno_set.count()

    @property
    def enquetes_relacionadas(self):
        # Isso pode ser uma propriedade mais complexa dependendo de como você relaciona áreas de interesse com enquetes.
        # Por enquanto, retornaremos 0.
        return 0

class AlunoInteresse(models.Model):
    aluno = models.ForeignKey(Aluno, verbose_name=_('Aluno'), on_delete=models.CASCADE)
    area_interesse = models.ForeignKey(AreaInteresse, verbose_name=_('Área de Interesse'), on_delete=models.CASCADE)
    data_adicao = models.DateTimeField(_('Data de Adição'), auto_now_add=True)
    nivel_interesse = models.IntegerField(_('Nível de Interesse'), default=1)
    observacoes = models.TextField(_('Observações'), blank=True, null=True)

    class Meta:
        verbose_name = _('Interesse do Aluno')
        verbose_name_plural = _('Interesses dos Alunos')
        unique_together = ('aluno', 'area_interesse')

    def __str__(self):
        return f"{self.aluno.nome} - {self.area_interesse.nome}"

    @property
    def nome_aluno(self):
        return self.aluno.nome

    @property
    def nome_area_interesse(self):
        return self.area_interesse.nome