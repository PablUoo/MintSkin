# Design do MintSkin (UI, UX e IHC)

## Identidade

| Elemento | Valor |
|---|---|
| Nome | MintSkin (proprietário: MintSkin) |
| Ícone do app | símbolo com o **m branco** sobre as três camadas amarelas |
| Logotipo | "mint" na cor do texto + "skin" em amarelo; versão clara e escura |
| Amarelo da marca | `#FFC400` (principal), `#FFD84A` (hover), `#FFF1A8` (camada clara) |
| Tinta | `#14151F` (texto no claro e fundo no escuro) |

A paleta completa, em versão clara e escura, está em `mintskin/ui/tema.py`.

## Regras de cor

- **Amarelo = ação principal.** Cada tela tem no máximo uma ação em amarelo
  ("Salvar visual atual", "Aplicar"). O resto usa botões neutros.
- **Texto sobre amarelo é sempre tinta** (`#14151F`), com contraste de cerca de 12:1.
  Branco sobre amarelo (≈1,6:1) só existe no logotipo, nunca em texto.
- **No tema claro, texto de destaque usa âmbar escuro** (`#8A5D00`), legível
  sobre branco (cerca de 5:1). O amarelo puro fica para fundos e bordas.
- O app tem **cor própria**: não muda quando a skin do desktop troca o tema GTK.
  O modo automático escolhe a versão clara ou escura conforme o tema do sistema.

## Estrutura da tela

```
┌───────────┬──────────────────────────────────────────────┐
│ logotipo  │  título da página                [busca]     │
│           │  explicação curta                            │
│ SKINS     │                                              │
│ Início    │  conteúdo da página                          │
│ Incluídas │                                              │
│ Minhas    │                                              │
│ MINTSKIN  │                                              │
│ Preferên. │                       [progresso / avisos]   │
│ Sobre     │                                              │
│ versão ©  │                                              │
└───────────┴──────────────────────────────────────────────┘
 barra: ↶ desfazer         MintSkin · página      Importar  [Salvar visual atual]
```

## Princípios de IHC aplicados

| Princípio | Como aparece |
|---|---|
| Visibilidade do estado do sistema | "Visual atual" no início; selo "Em uso"; contadores na lateral; barra de progresso em toda ação longa |
| Correspondência com o mundo real | textos em português simples ("Salvar visual atual", "Duplicar para personalizar"), sem jargão técnico |
| Controle e liberdade do usuário | **Desfazer** sempre visível; aviso com "Desfazer" depois de cada troca |
| Prevenção de erros | backup obrigatório antes da primeira troca; confirmação antes de excluir ou regravar; skins padrão bloqueadas com cadeado |
| Consistência | mesma posição para a ação principal; mesmo card para toda skin; mesmos três estilos de botão |
| Reconhecer em vez de lembrar | capa de cada skin; responsável ("por MintSkin" / "por você") e data no card |
| Estética e minimalismo | uma ação principal por tela; opções raras ficam no menu ⋯ ou em Preferências → Avançado |
| Ajuda a reconhecer erros | mensagens dizem o que houve e o que fazer ("Use Duplicar para criar uma cópia sua") |

## Acessibilidade

- Contraste de texto: pelo menos 4,5:1 nos dois temas.
- Foco do teclado visível (contorno amarelo) em todos os botões.
- Ícones sempre acompanhados de texto ou dica (*tooltip*).
- Logotipo desenhado na escala da tela, nítido em monitores HiDPI.
