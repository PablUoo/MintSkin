"""Regras do MintSkin testadas com adaptadores falsos (sem tocar no desktop).

    python3 -m unittest discover -s tests
"""
import unittest
from contextlib import contextmanager
from datetime import datetime

from mintskin.aplicacao.servico import ServicoSkins
from mintskin.dominio.erros import BackupNecessario, NadaParaDesfazer, SkinSomenteLeitura
from mintskin.dominio.preferencias import Preferencias
from mintskin.dominio.skin import AUTOR_MINTSKIN, Origem, Skin


class RepoFalso:
    def __init__(self, skins):
        self.skins = {s.id: s for s in skins}
        self.desfazer = None
        self.capas = {}

    def listar(self):
        return list(self.skins.values())

    def novo_id(self, nome):
        base, i, s = nome.lower().replace(" ", "-"), 2, nome.lower().replace(" ", "-")
        while s in self.skins:
            s, i = f"{base}-{i}", i + 1
        return s

    def gravar(self, skin, preencher=None, capa=None):
        assert not skin.incluida
        if preencher:
            preencher("/pasta/falsa")
        self.skins[skin.id] = skin
        return skin

    def copiar(self, origem, nova):
        self.skins[nova.id] = nova
        return nova

    def excluir(self, skin):
        del self.skins[skin.id]

    def definir_capa(self, skin, png):
        self.capas[skin.id] = png

    def exportar(self, skin, arquivo):
        return arquivo

    def importar(self, caminho, autor):
        s = Skin(id="importada", nome="Importada", origem=Origem.USUARIO, autor=autor)
        self.skins[s.id] = s
        return s

    def gravar_desfazer(self, preencher, estava_ativa):
        preencher("/pasta/desfazer")
        self.desfazer = Skin(id="desfazer", nome="Visual anterior", origem=Origem.USUARIO,
                             extras={"estava_ativa": estava_ativa})

    def desfazer_disponivel(self):
        return self.desfazer

    @contextmanager
    def desfazer_temporario(self):
        yield self.desfazer


class DesktopFalso:
    def __init__(self):
        self.na_tela = None          # id da skin "que esta na tela"
        self.aplicadas = []

    def verificar(self):
        pass

    def capturar(self, destino, leve=False, progresso=None):
        return True

    def aplicar(self, skin, prefs, progresso=None):
        self.aplicadas.append(skin.id)
        self.na_tela = skin.id if skin.id != "desfazer" else None
        return []

    def corresponde(self, skin):
        return skin.id == self.na_tela

    def restaurar_tela_login(self):
        pass


class EstadoFalso:
    def __init__(self):
        self.ativa, self.prefs = None, Preferencias()

    def skin_ativa(self):
        return self.ativa

    def definir_ativa(self, sid):
        self.ativa = sid

    def preferencias(self):
        return self.prefs

    def gravar_preferencias(self, p):
        self.prefs = p


def mac():
    return Skin(id="macos", nome="macOS Tahoe", origem=Origem.MINTSKIN, autor="Qualquer",
                criado_em=datetime(2026, 9, 22))


def minha(nome="Meu Mint", dia=22):
    return Skin(id=nome.lower().replace(" ", "-"), nome=nome, origem=Origem.USUARIO,
                criado_em=datetime(2026, 9, dia), atualizado_em=datetime(2026, 9, dia))


class Base(unittest.TestCase):
    def montar(self, *skins, na_tela=None):
        self.repo, self.desktop, self.estado = RepoFalso(skins), DesktopFalso(), EstadoFalso()
        self.desktop.na_tela = na_tela
        self.servico = ServicoSkins(self.repo, self.desktop, self.estado, "Pablo Almeida")
        return self.servico


class SkinsIncluidas(Base):
    def test_responsavel_e_sempre_mintskin(self):
        s = self.montar(mac())
        self.assertEqual(s.incluidas()[0].responsavel, AUTOR_MINTSKIN)

    def test_nao_pode_editar_trocar_capa_atualizar_nem_excluir(self):
        s = self.montar(mac())
        skin = s.obter("macos")
        for acao in (lambda: s.editar(skin, "Outro", ""),
                     lambda: s.trocar_capa(skin, "/x.png"),
                     lambda: s.atualizar_com_atual(skin),
                     lambda: s.excluir(skin)):
            with self.assertRaises(SkinSomenteLeitura):
                acao()
        self.assertEqual(skin.nome, "macOS Tahoe")
        self.assertEqual(self.repo.capas, {})

    def test_duplicar_cria_copia_do_usuario(self):
        s = self.montar(mac())
        copia = s.duplicar(s.obter("macos"), "Meu mac")
        self.assertTrue(copia.editavel)
        self.assertEqual(copia.responsavel, "Pablo Almeida")
        self.assertEqual(copia.baseada_em, "macOS Tahoe")
        s.editar(copia, "Meu mac 2", "ok")          # a copia pode ser editada

    def test_listas_separadas(self):
        s = self.montar(mac(), minha("Antiga", 1), minha("Nova", 30))
        self.assertEqual([x.id for x in s.incluidas()], ["macos"])
        self.assertEqual([x.nome for x in s.do_usuario()], ["Nova", "Antiga"])

    def test_skin_do_usuario_sem_autor_recebe_o_usuario(self):
        s = self.montar(minha())
        self.assertEqual(s.do_usuario()[0].responsavel, "Pablo Almeida")


class BackupNaPrimeiraTroca(Base):
    def test_sem_backup_nao_aplica(self):
        s = self.montar(mac())                       # instalacao nova, Mint na tela
        self.assertTrue(s.precisa_backup())
        with self.assertRaises(BackupNecessario):
            s.aplicar(s.obter("macos"))
        self.assertEqual(self.desktop.aplicadas, [])

    def test_depois_de_salvar_aplica(self):
        s = self.montar(mac())
        s.salvar_atual("Meu Mint original")
        self.assertFalse(s.precisa_backup())
        s.aplicar(s.obter("macos"))
        self.assertEqual(self.desktop.aplicadas, ["macos"])

    def test_com_skin_padrao_na_tela_nao_precisa(self):
        s = self.montar(mac(), na_tela="macos")
        self.assertFalse(s.precisa_backup())

    def test_com_skin_propria_nao_precisa(self):
        s = self.montar(mac(), minha())
        self.assertFalse(s.precisa_backup())


class Desfazer(Base):
    def test_sem_troca_nao_desfaz(self):
        s = self.montar(mac(), minha())
        with self.assertRaises(NadaParaDesfazer):
            s.desfazer()

    def test_desfazer_volta_a_skin_ativa(self):
        s = self.montar(mac(), minha(), na_tela="meu-mint")
        self.estado.ativa = "meu-mint"
        s.aplicar(s.obter("macos"))
        self.assertEqual(self.estado.ativa, "macos")
        s.desfazer()
        self.assertEqual(self.estado.ativa, "meu-mint")
        self.assertEqual(self.desktop.aplicadas, ["macos", "desfazer"])

    def test_excluir_a_ativa_limpa_o_estado(self):
        s = self.montar(minha())
        self.estado.ativa = "meu-mint"
        s.excluir(s.obter("meu-mint"))
        self.assertIsNone(self.estado.ativa)


if __name__ == "__main__":
    unittest.main()
