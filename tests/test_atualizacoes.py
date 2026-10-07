import tempfile
import unittest
from pathlib import Path

from mintskin.aplicacao.servico_atualizacoes import ServicoAtualizacoes
from mintskin.dominio.versao import NovaVersao, mais_nova
from mintskin.infra.estado import EstadoArquivo


class FonteFalsa:
    def __init__(self, nova):
        self.nova, self.consultas, self.instalados = nova, 0, []

    def ultima_versao(self):
        self.consultas += 1
        return self.nova

    def baixar(self, nova, destino):
        p = Path(destino) / "mintskin.deb"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("deb")
        return p

    def instalar(self, pacote):
        self.instalados.append(Path(pacote).name)


class Versoes(unittest.TestCase):
    def test_comparacao(self):
        self.assertTrue(mais_nova("v1.0.1", "1.0.0"))
        self.assertTrue(mais_nova("1.10.0", "1.9.9"))
        self.assertFalse(mais_nova("v1.0.0", "1.0.0"))
        self.assertFalse(mais_nova("lixo", "1.0.0"))


class Servico(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        self.fonte = FonteFalsa(NovaVersao("1.1.0", pacote_url="x", pacote_nome="mintskin_1.1.0_all.deb"))
        self.s = ServicoAtualizacoes(self.fonte, EstadoArquivo(self.raiz / "cfg"), self.raiz / "dl")

    def tearDown(self):
        self._tmp.cleanup()

    def test_consulta_no_maximo_a_cada_12h(self):
        self.assertEqual(self.s.verificar().versao, "1.1.0")
        self.assertIsNone(self.s.verificar())
        self.assertEqual(self.fonte.consultas, 1)
        self.assertIsNotNone(self.s.verificar(forcar=True))

    def test_versao_ignorada_nao_volta(self):
        self.s.ignorar(self.s.verificar())
        self.s.estado.gravar_valor("atualizacao_verificada_em", None)
        self.assertIsNone(self.s.verificar())
        self.assertIsNotNone(self.s.verificar(forcar=True))   # "verificar agora" sempre mostra

    def test_atualizar_instala_e_limpa(self):
        self.s.atualizar(self.s.verificar())
        self.assertEqual(self.fonte.instalados, ["mintskin.deb"])
        self.assertFalse((self.raiz / "dl" / "mintskin.deb").exists())


if __name__ == "__main__":
    unittest.main()
