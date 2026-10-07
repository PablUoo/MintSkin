class MintSkinErro(Exception):
    """Erro esperado, com mensagem pronta para mostrar ao usuario."""


class SkinSomenteLeitura(MintSkinErro):
    pass


class SkinNaoEncontrada(MintSkinErro):
    pass


class SkinInvalida(MintSkinErro):
    pass


class AmbienteIncompativel(MintSkinErro):
    pass


class NadaParaDesfazer(MintSkinErro):
    pass


class BackupNecessario(MintSkinErro):
    """Primeira troca: o visual atual precisa ser salvo antes de qualquer mudanca."""


class LoginNecessario(MintSkinErro):
    pass


class CredenciaisInvalidas(MintSkinErro):
    pass


class DadosInvalidos(MintSkinErro):
    pass


class SemPermissao(MintSkinErro):
    pass
