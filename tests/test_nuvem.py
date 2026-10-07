"""Conta, galeria e favoritos com os adaptadores reais em pastas temporarias.

As senhas abaixo sao valores de teste, criados so para estes testes.
"""
import json
import tempfile
import unittest
from pathlib import Path

from mintskin.aplicacao.servico import ServicoSkins
from mintskin.aplicacao.servico_nuvem import ServicoNuvem
from mintskin.dominio.erros import (CredenciaisInvalidas, DadosInvalidos, LoginNecessario,
                                    SemPermissao, SkinNaoEncontrada)
from mintskin.infra.estado import EstadoArquivo
from mintskin.infra.nuvem_local import NuvemLocal
from mintskin.infra.repositorio import RepositorioArquivos, gravar_meta

SENHA_TESTE = "senha-de-teste-123"


class DesktopFalso:
    def verificar(self): pass
    def capturar(self, destino, leve=False, progresso=None):
        Path(destino, "perfil.conf").write_text("org.cinnamon\tpanels-enabled\t['1:0:top']\n")
        return False
    def aplicar(self, skin, prefs, progresso=None): return []
    def corresponde(self, skin): return False
    def restaurar_tela_login(self): pass


class Maquina:
    """Uma 'maquina' (pastas proprias) apontando para a mesma nuvem."""

    def __init__(self, raiz, nuvem, usuario):
        oficiais = raiz / "oficiais"
        (oficiais / "macos").mkdir(parents=True, exist_ok=True)
        (oficiais / "macos" / "perfil.conf").write_text("x\ty\tz\n")
        gravar_meta(oficiais / "macos", {"id": "macos", "nome": "macOS Tahoe"})
        repo = RepositorioArquivos(raiz / usuario / "skins", [oficiais], raiz / usuario / "desfazer")
        self.estado = EstadoArquivo(raiz / usuario / "config")
        self.skins = ServicoSkins(repo, DesktopFalso(), self.estado, usuario)
        self.nuvem = ServicoNuvem(nuvem, self.estado, self.skins)


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        raiz = Path(self._tmp.name)
        self.servidor = NuvemLocal(raiz / "nuvem")
        self.ana = Maquina(raiz, self.servidor, "ana")
        self.bia = Maquina(raiz, self.servidor, "bia")

    def tearDown(self):
        self._tmp.cleanup()

    def skin_da_ana(self, nome="Tema da Ana"):
        return self.ana.skins.salvar_atual(nome, "escuro com dock")


class Contas(Base):
    def test_criar_entrar_sair(self):
        n = self.ana.nuvem
        conta = n.criar_conta("Ana Souza", "Ana@Exemplo.com", SENHA_TESTE)
        self.assertEqual(conta.email, "ana@exemplo.com")
        self.assertEqual(conta.iniciais, "AS")
        n.sair()
        self.assertIsNone(n.conta())
        self.assertEqual(n.entrar("ana@exemplo.com", SENHA_TESTE).nome, "Ana Souza")

    def test_senha_errada(self):
        self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        with self.assertRaises(CredenciaisInvalidas):
            self.bia.nuvem.entrar("ana@exemplo.com", "outra-senha-123")

    def test_validacoes(self):
        for nome, email, senha in (("A", "a@b.co", SENHA_TESTE), ("Ana", "sem-arroba", SENHA_TESTE),
                                   ("Ana", "ana@exemplo.com", "curta")):
            with self.assertRaises(DadosInvalidos):
                self.ana.nuvem.criar_conta(nome, email, senha)

    def test_email_repetido(self):
        self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        with self.assertRaises(DadosInvalidos):
            self.bia.nuvem.criar_conta("Outra", "ANA@exemplo.com", SENHA_TESTE)

    def test_senha_nunca_fica_em_texto(self):
        self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        arquivo = self.servidor.raiz / "contas.json"
        self.assertNotIn(SENHA_TESTE, arquivo.read_text())
        self.assertEqual(arquivo.stat().st_mode & 0o777, 0o600)


class Galeria(Base):
    def test_oficiais_sempre_aparecem_e_ja_estao_instaladas(self):
        itens = self.bia.nuvem.galeria("oficiais")
        self.assertEqual([i.nome for i in itens], ["macOS Tahoe"])
        self.assertTrue(itens[0].oficial and itens[0].instalada)
        self.assertEqual(itens[0].autor_nome, "MintSkin")

    def test_enviar_exige_login(self):
        with self.assertRaises(LoginNecessario):
            self.ana.nuvem.enviar(self.skin_da_ana(), publica=True)

    def test_privada_nao_aparece_na_galeria(self):
        self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        item = self.ana.nuvem.enviar(self.skin_da_ana(), publica=False)
        self.assertEqual([i.id for i in self.ana.nuvem.da_conta()], [item.id])
        self.assertEqual(self.bia.nuvem.galeria("comunidade"), [])
        with self.assertRaises(SkinNaoEncontrada):
            self.bia.nuvem.item(item.id)

    def test_publicar_baixar_em_outra_maquina(self):
        self.ana.nuvem.criar_conta("Ana Souza", "ana@exemplo.com", SENHA_TESTE)
        item = self.ana.nuvem.enviar(self.skin_da_ana(), publica=True)
        na_galeria = self.bia.nuvem.galeria("comunidade")
        self.assertEqual([i.nome for i in na_galeria], ["Tema da Ana"])
        self.assertFalse(na_galeria[0].instalada)

        skin = self.bia.nuvem.baixar(na_galeria[0])
        self.assertEqual(skin.responsavel, "Ana Souza")    # o autor continua sendo a Ana
        self.assertTrue(skin.editavel)
        self.assertNotIn("nuvem_id", skin.extras)          # a copia nao e da Bia na nuvem
        self.assertTrue(self.bia.nuvem.item(item.id).instalada)
        self.assertEqual(self.bia.nuvem.item(item.id).downloads, 1)

    def test_reenviar_atualiza_a_mesma_skin(self):
        self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        skin = self.skin_da_ana()
        primeiro = self.ana.nuvem.enviar(skin, publica=False)
        segundo = self.ana.nuvem.enviar(self.ana.skins.obter(skin.id), publica=True)
        self.assertEqual(primeiro.id, segundo.id)
        self.assertTrue(self.ana.nuvem.item(primeiro.id).publica)

    def test_so_o_dono_altera(self):
        self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        item = self.ana.nuvem.enviar(self.skin_da_ana(), publica=True)
        self.bia.nuvem.criar_conta("Bia", "bia@exemplo.com", SENHA_TESTE)
        with self.assertRaises(SemPermissao):
            self.bia.nuvem.remover(item)
        with self.assertRaises(SemPermissao):
            self.bia.nuvem.definir_publica(item, False)

    def test_favoritar_e_contar(self):
        self.bia.nuvem.criar_conta("Bia", "bia@exemplo.com", SENHA_TESTE)
        mac = self.bia.nuvem.galeria("oficiais")[0]
        self.bia.nuvem.favoritar(mac, True)
        favoritas = self.bia.nuvem.galeria("favoritas")
        self.assertEqual([i.id for i in favoritas], [mac.id])
        self.assertEqual(favoritas[0].favoritos, 1)
        self.bia.nuvem.favoritar(mac, False)
        self.assertEqual(self.bia.nuvem.galeria("favoritas"), [])

    def test_favoritar_exige_login(self):
        with self.assertRaises(LoginNecessario):
            self.bia.nuvem.favoritar(self.bia.nuvem.galeria()[0], True)

    def test_perfil_mostra_so_publicas(self):
        conta = self.ana.nuvem.criar_conta("Ana", "ana@exemplo.com", SENHA_TESTE)
        self.ana.nuvem.enviar(self.skin_da_ana("Publica"), publica=True)
        self.ana.nuvem.enviar(self.skin_da_ana("Secreta"), publica=False)
        perfil = self.bia.nuvem.perfil(conta.id)
        self.assertEqual([i.nome for i in perfil.itens], ["Publica"])
        self.assertTrue(self.bia.nuvem.perfil("mintskin").oficial)

    def test_busca(self):
        self.assertEqual(len(self.bia.nuvem.galeria(busca="tahoe")), 1)
        self.assertEqual(self.bia.nuvem.galeria(busca="nada-disso"), [])


if __name__ == "__main__":
    unittest.main()
