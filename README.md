<img src="static/assets/img/logo_white.svg" width="300" height="400">

## Sobre
Gabarita IF é um sistema educacional desenvolvido para apoiar estudantes na preparação para o Exame de Seleção do Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Norte (IFRN). O software mantém uma base de dados com questões de processos seletivos anteriores divulgados pelo IFRN e disponibiliza todos os simuladões já realizados pelo Meta IFRN.

Esta plataforma é resultado da elaboração de um projeto de pesquisa realizado na disciplina intitulada "Desenvolvimento de Projeto Integrador" do curso Técnico Integrado ao Ensino Médio de Informática para Internet do IFRN – Campus São Paulo do Potengi.

## Tecnologias Utilizadas
[![SkillIcons](https://skillicons.dev/icons?i=js,py,html,css,django,bootstrap)](https://skillicons.dev)<br/>

## Integrantes
- Anna Beatriz
- Gabriela Maia

## Rodando
Siga as instruções abaixo para configurar o ambiente do projeto após clonar o repositório.

### 1. Criando e Ativando o Ambiente Virtual
```bash
python -m venv venv  
venv\Scripts\Activate.ps1
```

### 2. Instalando as Dependências
```bash
pip install -r requirements.txt  
```

### 3. Aplicando as Migrações
```bash
python manage.py migrate  
```

### 4. Criando um Superusuário
```bash
python manage.py createsuperuser  
```

Siga as instruções e defina um nome de usuário, e-mail e senha.

### 5. Executando o Servidor

```bash
python manage.py runserver  
```

### 6. Acessando o Django Admin

Abra o navegador e acesse:

```
http://127.0.0.1:8000/admin/
```

Faça login com o superusuário criado anteriormente.

Agora o **Gabarita** está pronto para ser utilizado!
