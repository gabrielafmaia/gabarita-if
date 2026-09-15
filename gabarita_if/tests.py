from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Caderno, Disciplina


User = get_user_model()


class CadernoDificuldadeTest(TestCase):
	def setUp(self):
		self.usuario = User.objects.create_user(
			username="usuario-teste",
			password="senha-teste",
		)
		self.disciplina = Disciplina.objects.create(nome="Matemática")
		self.client.force_login(self.usuario)

	def dados_formulario(self, dificuldades, nome="Caderno teste"):
		return {
			"nome": nome,
			"cor": "#4cc49e",
			"blocos[0][disciplina]": str(self.disciplina.pk),
			"blocos[0][assunto]": "",
			"blocos[0][quantidade]": "1",
			"dificuldade": dificuldades,
		}

	def editar(self, dificuldades, nome="Caderno editado"):
		caderno = Caderno.objects.create(
			nome="Caderno original",
			usuario=self.usuario,
			disciplina=self.disciplina,
			dificuldade=["Fácil"],
		)
		resposta = self.client.post(
			reverse("gabarita_if:ajax-editar-caderno", args=[caderno.pk]),
			self.dados_formulario(dificuldades, nome),
			HTTP_HX_REQUEST="true",
		)
		caderno.refresh_from_db()
		return caderno, resposta

	def test_criacao_persiste_multiplas_dificuldades(self):
		resposta = self.client.post(
			reverse("gabarita_if:ajax-criar-caderno"),
			self.dados_formulario(["Fácil", "Média", "Difícil"]),
			HTTP_HX_REQUEST="true",
		)

		self.assertEqual(resposta.status_code, 200)
		self.assertEqual(
			list(Caderno.objects.get(nome="Caderno teste").dificuldade),
			["Fácil", "Média", "Difícil"],
		)

	def test_criacao_aceita_todas_as_combinacoes(self):
		combinacoes = [
			[],
			["Fácil"],
			["Média"],
			["Difícil"],
			["Fácil", "Média"],
			["Fácil", "Difícil"],
			["Média", "Difícil"],
			["Fácil", "Média", "Difícil"],
		]

		for indice, dificuldades in enumerate(combinacoes):
			nome = f"Caderno combinação {indice}"
			resposta = self.client.post(
				reverse("gabarita_if:ajax-criar-caderno"),
				self.dados_formulario(dificuldades, nome),
				HTTP_HX_REQUEST="true",
			)

			self.assertEqual(resposta.status_code, 200)
			self.assertEqual(
				Caderno.objects.get(nome=nome).dificuldade,
				dificuldades,
			)

	def test_edicao_atualiza_multiplas_dificuldades(self):
		caderno, resposta = self.editar(["Fácil", "Média"])

		self.assertEqual(resposta.status_code, 200)
		self.assertEqual(caderno.nome, "Caderno editado")
		self.assertEqual(caderno.dificuldade, ["Fácil", "Média"])

		resposta = self.client.post(
			reverse("gabarita_if:ajax-editar-caderno", args=[caderno.pk]),
			self.dados_formulario(["Difícil"], "Caderno final"),
			HTTP_HX_REQUEST="true",
		)
		caderno.refresh_from_db()

		self.assertEqual(resposta.status_code, 200)
		self.assertEqual(caderno.nome, "Caderno final")
		self.assertEqual(caderno.dificuldade, ["Difícil"])

	def test_edicao_marca_dificuldades_salvas(self):
		caderno = Caderno.objects.create(
			nome="Caderno salvo",
			usuario=self.usuario,
			disciplina=self.disciplina,
			dificuldade=["Fácil", "Média"],
		)

		resposta = self.client.get(
			reverse("gabarita_if:ajax-editar-caderno", args=[caderno.pk]),
			HTTP_HX_REQUEST="true",
		)

		self.assertEqual(resposta.status_code, 200)
		conteudo = resposta.content.decode()
		self.assertIn('id="dificuldade_facil"', conteudo)
		self.assertIn('id="dificuldade_media"', conteudo)
		self.assertIn('id="dificuldade_dificil"', conteudo)
		self.assertEqual(conteudo.count('name="dificuldade"'), 3)

		facil = conteudo.index('id="dificuldade_facil"')
		media = conteudo.index('id="dificuldade_media"')
		dificil = conteudo.index('id="dificuldade_dificil"')
		self.assertIn("checked", conteudo[facil:media])
		self.assertIn("checked", conteudo[media:dificil])
		self.assertNotIn("checked", conteudo[dificil:dificil + 150])

	def test_adicionar_bloco_htmx_nao_reintroduz_dificuldade(self):
		resposta = self.client.get(
			reverse("gabarita_if:ajax-adicionar-bloco"),
			{"index": 1},
			HTTP_HX_REQUEST="true",
		)

		self.assertEqual(resposta.status_code, 200)
		conteudo = resposta.content.decode()
		self.assertIn('blocos[1][disciplina]', conteudo)
		self.assertNotIn("dificuldade", conteudo)

# Create your tests here.
