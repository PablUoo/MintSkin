# Arquitetura do MintSkin

O MintSkin usa **Arquitetura Limpa** (*Clean Architecture*) no formato de
**Portas e Adaptadores** (*arquitetura hexagonal*), com **injeção de
dependência manual** numa raiz de composição.

A regra é uma só: **as dependências apontam para dentro.** O domínio não sabe
que existe GTK, gsettings ou disco. A interface não sabe que existe gsettings.

```
          ui/ (GTK)        cli.py
              \             /
               v           v
            aplicacao/  (casos de uso + portas)
                   |
                   v
               dominio/  (Skin e regras)
                   ^
                   |  implementa as portas
               infra/  (disco, gsettings, Cinnamon, Plank, capas)

  composicao.py: o único lugar que conhece todos e liga infra -> aplicacao
```

## Camadas

| Camada | Pasta | O que tem | Depende de |
|---|---|---|---|
| Domínio | `mintskin/dominio/` | `Skin`, `Origem`, `Preferencias`, erros. Regras como "skin incluída não é editável" e "o responsável das incluídas é o MintSkin". | nada |
| Aplicação | `mintskin/aplicacao/` | `ServicoSkins` (aplicar, salvar, duplicar, desfazer, backup na primeira troca), `ServicoNuvem` (conta, galeria, favoritos, enviar e baixar) e `ServicoAtualizacoes`. As **portas** ficam em `portas.py`: `RepositorioSkins`, `Desktop`, `Estado`, `Migrador`, `Nuvem`, `Atualizacoes`. | domínio |
| Infraestrutura | `mintskin/infra/` | Adaptadores: `RepositorioArquivos` (pastas e `.mintskin`), `DesktopCinnamon` (gsettings, applets, temas, Plank, tela de login), `NuvemLocal` (contas e galeria nesta máquina), `AtualizadorGitHub` (Releases), `EstadoArquivo`, `MigradorMacSh`, `GeradorCapas`. | domínio, aplicação |
| Interface | `mintskin/ui/`, `mintskin/cli.py` | Janela GTK (com a marca e a paleta em `ui/tema.py` e `ui/marca/`) e linha de comando. Só chamam o `ServicoSkins`. | domínio, aplicação |
| Composição | `mintskin/composicao.py` | `montar()`: cria os adaptadores e injeta no serviço. | todas |

## Onde ficam as regras

Toda regra de "pode / não pode" mora no domínio ou no serviço. A interface
apenas esconde botões que não se aplicam:

- **Skins incluídas no MintSkin** (`Origem.MINTSKIN`) não podem ser renomeadas,
  ter a capa trocada, ser atualizadas nem excluídas: `Skin.exigir_editavel()`
  lança `SkinSomenteLeitura`. O repositório tem uma segunda barreira e se recusa
  a gravar nelas. Para personalizar, o usuário duplica: a cópia vira dele.
- **Responsável**: `Skin.responsavel` é sempre "MintSkin" para as incluídas e o
  nome do usuário (campo GECOS da conta) para as dele.
- **Backup na primeira troca**: `ServicoSkins.aplicar()` lança
  `BackupNecessario` enquanto o usuário não tiver nenhuma skin própria e o
  visual da tela não for uma skin conhecida. A janela abre então o diálogo
  "Salve seu visual atual primeiro" e aplica a skin escolhida depois de salvar.
- **Desfazer**: antes de cada troca o serviço pede ao desktop uma captura leve
  do visual atual; desfazer reaplica essa captura.

## Por que essa arquitetura

- **Testável sem mexer no desktop.** `tests/test_servico.py` roda as regras com
  adaptadores falsos em memória, em milissegundos, sem gsettings nem Cinnamon.
  O `build-deb.sh` roda esses testes e não gera o pacote se algum falhar.
- **Trocar uma peça não espalha mudança.** A nuvem de verdade será um novo
  adaptador da porta `Nuvem` (veja [NUVEM.md](NUVEM.md)); suporte a outro
  desktop (MATE, Xfce), um novo adaptador de `Desktop`. Janela e regras não mudam.
- **Interface e CLI fazem a mesma coisa**, porque as duas passam pelo mesmo serviço.

## Rodando os testes

```bash
python3 -m unittest discover -s tests -v
```
