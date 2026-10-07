# Conta e nuvem

Hoje a conta, a galeria e as skins enviadas ficam **neste computador**, em
`~/.local/share/mintskin/nuvem/`. A aplicação já fala com essa "nuvem" pela
porta `Nuvem` (`mintskin/aplicacao/portas.py`). Para ir para a nuvem de verdade,
basta escrever um adaptador novo com os mesmos métodos e trocá-lo em
`mintskin/composicao.py`. Nada na interface ou nas regras muda.

## O que existe hoje (`infra/nuvem_local.py`)

| Arquivo | Conteúdo |
|---|---|
| `contas.json` | nome, e-mail e senha em hash PBKDF2-SHA256 (240 mil iterações, sal por conta). Permissão 600. |
| `sessoes.json` | token de sessão → conta. Permissão 600. |
| `favoritos.json` | conta → skins favoritas |
| `itens/<id>/` | `item.json` (dono, pública ou privada, downloads) e a cópia da skin |

## Servidor sugerido

API HTTPS simples, com os mesmos verbos da porta:

| Método | Rota | Porta |
|---|---|---|
| POST | `/contas` | `criar_conta` |
| POST | `/sessoes` | `entrar` (devolve um token) |
| DELETE | `/sessoes/atual` | `sair` |
| GET | `/eu` | `conta` |
| GET | `/galeria` | `galeria` (só públicas) |
| GET | `/eu/skins` | `da_conta` |
| POST / PUT | `/skins` · `/skins/{id}` | `enviar` (upload do `.mintskin`) |
| GET | `/skins/{id}` · `/skins/{id}/arquivo` | `item` · `baixar` |
| PATCH | `/skins/{id}` | `definir_publica` |
| DELETE | `/skins/{id}` | `remover` |
| PUT / DELETE | `/eu/favoritos/{id}` | `favoritar` |
| GET | `/autores/{id}` | `perfil` |

Pontos de atenção para a versão online:

- **Login:** OAuth com GitHub/Google evita guardar senhas. Se tiver senha,
  use Argon2 ou bcrypt no servidor e limite tentativas.
- **Token:** guardar no chaveiro do sistema (libsecret), não em arquivo.
- **Arquivos:** guardar os `.mintskin` num armazenamento de objetos (S3, R2) e
  servir por link temporário.
- **Moderação:** skins públicas trazem temas e ícones de terceiros. Prever
  denúncia, limite de tamanho e verificação do conteúdo do pacote.
- **Migração:** na primeira vez online, oferecer enviar as skins da conta local.
