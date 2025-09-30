from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMINISTRACAO = "administracao"
    AGRICULTURA = "agricultura"
    AGROECOLOGIA = "agroecologia"
    AGROPECUARIA = "agropecuaria"
    ALIMENTOS = "alimentos"
    APICULTURA = "apicultura"
    BIOCOMBUSTIVEIS = "biocombustiveis"
    COMERCIO = "comercio"
    CONTROLE_AMBIENTAL = "controle_ambiental"
    EDIFICACOES = "edificacoes"
    ELETROMECANICA = "eletromecanica"
    ELETRONICA = "eletronica"
    ELETROTECNICA = "eletrotecnica"
    EQUIPAMENTOS_BIOMEDICOS = "equipamentos_biomedicos"
    EVENTOS = "eventos"
    GEOLOGIA = "geologia"
    INFORMATICA = "informatica"
    INFORMATICA_INTERNET = "informatica_internet"
    JOGOS_DIGITAIS = "jogos_digitais"
    LAZER = "lazer"
    LOGISTICA = "logistica"
    MANUTENCAO_INFORMATICA = "manutencao_informatica"
    MECANICA = "mecanica"
    MECATRONICA = "mecatronica"
    MEIO_AMBIENTE = "meio_ambiente"
    MINERACAO = "mineracao"
    MULTIMIDIA = "multimidia"
    QUIMICA = "quimica"
    RECURSOS_PESQUEIROS = "recursos_pesqueiros"
    REFRIGERACAO_CLIMATIZACAO = "refrigeracao_climatizacao"
    TEXTIL = "textil"
    VESTUARIO = "vestuario"
    ZOOTECNIA = "zootecnia"

    CURSOS = [
        (ADMINISTRACAO, "Administração"),
        (AGRICULTURA, "Agricultura"),
        (AGROECOLOGIA, "Agroecologia"),
        (AGROPECUARIA, "Agropecuária"),
        (ALIMENTOS, "Alimentos"),
        (APICULTURA, "Apicultura"),
        (BIOCOMBUSTIVEIS, "Biocombustíveis"),
        (COMERCIO, "Comércio"),
        (CONTROLE_AMBIENTAL, "Controle Ambiental"),
        (EDIFICACOES, "Edificações"),
        (ELETROMECANICA, "Eletromecânica"),
        (ELETRONICA, "Eletrônica"),
        (ELETROTECNICA, "Eletrotécnica"),
        (EQUIPAMENTOS_BIOMEDICOS, "Equipamentos Biomédicos"),
        (EVENTOS, "Eventos"),
        (GEOLOGIA, "Geologia"),
        (INFORMATICA, "Informática"),
        (INFORMATICA_INTERNET, "Informática para Internet"),
        (JOGOS_DIGITAIS, "Jogos Digitais"),
        (LAZER, "Lazer"),
        (LOGISTICA, "Logística"),
        (MANUTENCAO_INFORMATICA, "Manutenção e Suporte em Informática"),
        (MECANICA, "Mecânica"),
        (MECATRONICA, "Mecatrônica"),
        (MEIO_AMBIENTE, "Meio Ambiente"),
        (MINERACAO, "Mineração"),
        (MULTIMIDIA, "Multimídia"),
        (QUIMICA, "Química"),
        (RECURSOS_PESQUEIROS, "Recursos Pesqueiros"),
        (REFRIGERACAO_CLIMATIZACAO, "Refrigeração e Climatização"),
        (TEXTIL, "Têxtil"),
        (VESTUARIO, "Vestuário"),
        (ZOOTECNIA, "Zootecnia"),
    ]


    PARTICULAR = "administracao"
    PÚBLICA = "agricultura"
    OUTRA = "outra"

    TIPOS_ESCOLA = [
        (PARTICULAR, "Particular"),
        (PÚBLICA, "Pública"),
        (OUTRA, "Outra"),
    ]


    MASCULINO = "masculino"
    FEMININO = "feminino"
    OUTRO = "outro"

    GENEROS = [
        (MASCULINO, "Masculino"),
        (FEMININO, "Feminino"),
        (OUTRO, "Outro"),
    ]

    idade = models.PositiveIntegerField(blank=True, null=True)
    genero = models.CharField(max_length=10, choices=GENEROS, blank=True, null=True)
    curso = models.CharField(max_length=50, choices=CURSOS, blank=True, null=True)
    tipo_escola = models.CharField(max_length=15, choices=TIPOS_ESCOLA, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to="users/foto_perfil/", blank=True, null=True)

    def __str__(self):
        return self.first_name