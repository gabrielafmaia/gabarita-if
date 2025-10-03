from django.db import models
from django.conf import settings

class Subject(models.Model):
    PORTUGUESE = "PORTUGUES"
    MATH = "MATEMATICA"

    SUBJECT_CHOICES = [
        (PORTUGUESE, "Português"),
        (MATH, "Matemática"),
    ]

    name = models.CharField(max_length=20, choices=SUBJECT_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    TIPOLOGIA_GENEROS = "TIPOLOGIA_GENEROS"
    INTERPRETACAO_TEXTO = "INTERPRETACAO_TEXTO"
    VARIACAO_LINGUISTICA = "VARIACAO_LINGUISTICA"
    FONETICA = "FONETICA"
    ACENTUACAO_PONTUACAO = "ACENTUACAO_PONTUACAO"
    CRASE = "CRASE"
    ESTRUTURA_PALAVRAS = "ESTRUTURA_PALAVRAS"
    FUNCOES_LINGUAGEM = "FUNCOES_LINGUAGEM"
    SEMANTICA = "SEMANTICA"
    CLASSES_PALAVRAS = "CLASSES_PALAVRAS"
    CONCORDANCIA = "CONCORDANCIA"
    REGENCIA = "REGENCIA"
    TIPOS_VERBOS = "TIPOS_VERBOS"
    FUNCOES_SINTATICAS = "FUNCOES_SINTATICAS"
    PERIODO_COMPOSTO = "PERIODO_COMPOSTO"
    USO_QUE_E_SE = "USO_QUE_E_SE"

    PORTUGUESE_TOPICS = [
        (TIPOLOGIA_GENEROS, "Tipologia e Gêneros Textuais"),
        (INTERPRETACAO_TEXTO, "Interpretação de Texto"),
        (VARIACAO_LINGUISTICA, "Variação Linguística"),
        (FONETICA, "Fonética"),
        (ACENTUACAO_PONTUACAO, "Acentuação Gráfica e Pontuação"),
        (CRASE, "Crase"),
        (ESTRUTURA_PALAVRAS, "Estrutura e Formação das Palavras"),
        (FUNCOES_LINGUAGEM, "Funções da Linguagem"),
        (SEMANTICA, "Semântica"),
        (CLASSES_PALAVRAS, "Classes de Palavras"),
        (CONCORDANCIA, "Concordância Nominal e Verbal"),
        (REGENCIA, "Regência Nominal e Verbal"),
        (TIPOS_VERBOS, "Tipos de Verbos"),
        (FUNCOES_SINTATICAS, "Funções Sintáticas"),
        (PERIODO_COMPOSTO, "Período Composto"),
        (USO_QUE_E_SE, 'Uso do Que e Se'),
    ]

    SISTEMA_NUMERACAO = "SISTEMA_NUMERACAO"
    CONJUNTOS_NUMERICOS = "CONJUNTOS_NUMERICOS"
    OPERACOES_FUNDAMENTAIS = "OPERACOES_FUNDAMENTAIS"
    MULTIPLOS_DIVISORES = "MULTIPLOS_DIVISORES"
    MMC_MDC = "MMC_MDC"
    FRACOES_DECIMAIS = "FRACOES_DECIMAIS"
    EXPRESSOES_ALGEBRICAS = "EXPRESSOES_ALGEBRICAS"
    UNIDADES_MEDIDA = "UNIDADES_MEDIDA"
    NOTACAO_CIENTIFICA = "NOTACAO_CIENTIFICA"
    POTENCIACAO_RADICACAO = "POTENCIACAO_RADICACAO"
    RAZAO_PROPORCAO = "RAZAO_PROPORCAO"
    REGRA_DE_TRES = "REGRA_DE_TRES"
    PORCENTAGEM = "PORCENTAGEM"
    GRAFICOS_PAR_ORDENADO = "GRAFICOS_PAR_ORDENADO"
    MEDIA_SIMPLES_PONDERADA = "MEDIA_SIMPLES_PONDERADA"
    ANGULOS_TRIANGULOS = "ANGULOS_TRIANGULOS"
    TEOREMA_TALES = "TEOREMA_TALES"
    TEOREMA_PITAGORAS = "TEOREMA_PITAGORAS"
    QUADRILATEROS = "QUADRILATEROS"
    CIRCULO_CIRCUNFERENCIA = "CIRCULO_CIRCUNFERENCIA"
    VOLUME_SOLIDOS = "VOLUME_SOLIDOS"
    PROBABILIDADE = "PROBABILIDADE"
    MEDIDAS_TEMPO = "MEDIDAS_TEMPO"
    EQUACAO_1_2_GRAU = "EQUACAO_1_2_GRAU"
    SISTEMA_EQUACOES = "SISTEMA_EQUACOES"
    JUROS_SIMPLES = "JUROS_SIMPLES"
    PRODUTOS_NOTAVEIS = "PRODUTOS_NOTAVEIS"
    CONSUMO_ENERGIA_ELETRICA = "CONSUMO_ENERGIA_ELETRICA"

    MATH_TOPICS = [
        (SISTEMA_NUMERACAO, "Sistema de Numeração"),
        (CONJUNTOS_NUMERICOS, "Conjuntos Numéricos"),
        (OPERACOES_FUNDAMENTAIS, "Operações Fundamentais"),
        (MULTIPLOS_DIVISORES, "Múltiplos e Divisores"),
        (MMC_MDC, "MMC e MDC"),
        (FRACOES_DECIMAIS, "Frações e Números Decimais"),
        (EXPRESSOES_ALGEBRICAS, "Expressões Algébricas"),
        (UNIDADES_MEDIDA, "Unidades de Medida"),
        (NOTACAO_CIENTIFICA, "Notação Científica"),
        (POTENCIACAO_RADICACAO, "Potenciação e Radiciação"),
        (RAZAO_PROPORCAO, "Razão e Proporção"),
        (REGRA_DE_TRES, "Regra de Três"),
        (PORCENTAGEM, "Porcentagem"),
        (GRAFICOS_PAR_ORDENADO, "Gráficos/Par Ordenado"),
        (MEDIA_SIMPLES_PONDERADA, "Média Simples e Ponderada"),
        (ANGULOS_TRIANGULOS, "Ângulos e Triângulos"),
        (TEOREMA_TALES, "Teorema de Tales"),
        (TEOREMA_PITAGORAS, "Teorema de Pitágoras"),
        (QUADRILATEROS, "Quadriláteros"),
        (CIRCULO_CIRCUNFERENCIA, "Círculo e Circunferência"),
        (VOLUME_SOLIDOS, "Volume de Sólidos"),
        (PROBABILIDADE, "Probabilidade"),
        (MEDIDAS_TEMPO, "Medidas de Tempo"),
        (EQUACAO_1_2_GRAU, "Equação do 1º e 2º Grau"),
        (SISTEMA_EQUACOES, "Sistema de Equações"),
        (JUROS_SIMPLES, "Juros Simples"),
        (PRODUTOS_NOTAVEIS, "Produtos Notáveis"),
        (CONSUMO_ENERGIA_ELETRICA, "Consumo de Energia Elétrica"),
    ]

    ALL_TOPICS = PORTUGUESE_TOPICS + MATH_TOPICS
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=ALL_TOPICS, default="")
    
    # ADICIONAR: método para obter choices baseadas no subject
    def get_topic_choices(self):
        if self.subject and self.subject.name == Subject.PORTUGUESE:
            return self.PORTUGUESE_TOPICS
        elif self.subject and self.subject.name == Subject.MATH:
            return self.MATH_TOPICS

    def __str__(self):
        return f"{self.get_name_display()} ({self.subject})"


class Assessment(models.Model):
    PRACTICE_TEST = "simulado"
    EXAM = "prova"

    ASSESSMENT_TYPES = [
        (PRACTICE_TEST, "Simulado"),
        (EXAM, "Prova")
    ]

    title = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=ASSESSMENT_TYPES)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.year})"
    

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT)
    text = models.TextField()
    text_solution = models.TextField()
    video_solution = models.FileField(upload_to='lists_pdfs/', blank=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
    

class Passage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='supporting_images/', blank=True, null=True)

    def __str__(self):
        return self.text


class CustomList(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SavedFilter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PDFList(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='lists_pdfs/')

    def __str__(self):
        return f"{self.subject} | {self.topic}"


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
