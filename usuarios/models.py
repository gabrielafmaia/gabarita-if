from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    CURSOS = [
        ("Administração", "Administração"),
        ("Agricultura", "Agricultura"),
        ("Agroecologia", "Agroecologia"),
        ("Agropecuária", "Agropecuária"),
        ("Alimentos", "Alimentos"),
        ("Apicultura", "Apicultura"),
        ("Biocombustíveis", "Biocombustíveis"),
        ("Comércio", "Comércio"),
        ("Controle Ambiental", "Controle Ambiental"),
        ("Edificações", "Edificações"),
        ("Eletromecânica", "Eletromecânica"),
        ("Eletrônica", "Eletrônica"),
        ("Eletrotécnica", "Eletrotécnica"),
        ("Equipamentos Biomédicos", "Equipamentos Biomédicos"),
        ("Estradas", "Estradas"),
        ("Eventos", "Eventos"),
        ("Geologia", "Geologia"),
        ("Guia de Turismo", "Guia de Turismo"),
        ("Informática", "Informática"),
        ("Informática para Internet", "Informática para Internet"),
        ("Instrumento Musical", "Instrumento Musical"),
        ("Jogos Digitais", "Jogos Digitais"),
        ("Lazer", "Lazer"),
        ("Logística", "Logística"),
        ("Manutenção e Suporte em Informática", "Manutenção e Suporte em Informática"),
        ("Mecânica", "Mecânica"),
        ("Mecatrônica", "Mecatrônica"),
        ("Meio Ambiente", "Meio Ambiente"),
        ("Mineração", "Mineração"),
        ("Multimídia", "Multimídia"),
        ("Petróleo e Gás", "Petróleo e Gás"),
        ("Química", "Química"),
        ("Recursos Pesqueiros", "Recursos Pesqueiros"),
        ("Redes de Computadores", "Redes de Computadores"),
        ("Refrigeração e Climatização", "Refrigeração e Climatização"),
        ("Saneamento", "Saneamento"),
        ("Secretaria Escolar", "Secretaria Escolar"),
        ("Segurança do Trabalho", "Segurança do Trabalho"),
        ("Segurança do Trabalho (a distância)", "Segurança do Trabalho (a distância)"),
        ("Técnico em Comércio", "Técnico em Comércio"),
        ("Técnico em Cooperativismo", "Técnico em Cooperativismo"),
        ("Técnico em Edificações", "Técnico em Edificações"),
        ("Técnico em Informática", "Técnico em Informática"),
        ("Técnico em Manutenção e Suporte em Informática", "Técnico em Manutenção e Suporte em Informática"),
        ("Têxtil", "Têxtil"),
        ("Vestuário", "Vestuário"),
        ("Zootecnia", "Zootecnia"),
    ]

    avatar = models.ImageField(upload_to="usuarios-avatar/", blank=True, null=True, verbose_name="Foto de Perfil")
    email = models.EmailField(max_length=200, unique=True, verbose_name="E-mail")
    first_name = models.CharField(max_length=150, verbose_name="Nome")
    last_name = models.CharField(max_length=150, verbose_name="Sobrenome")
    curso = models.CharField(max_length=50, choices=CURSOS, blank=True, null=True)
   
    # Define qual o campo é o nome de usuário
    USERNAME_FIELD = "email"
    # Necessário para createsuperuser continuar funcionando
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.first_name