# Play Ouro

Biblioteca local para organizar e abrir jogos clássicos em Flash (`.swf`) no Windows. O launcher usa o Flash Player standalone que acompanha o projeto, sem depender do navegador.

`play.py` é a versão oficial do programa. Ele nunca renomeia, move ou altera os arquivos dentro de `JOGOS`.

## Destaques

- Interface escura, limpa e responsiva, com visual neon discreto.
- Biblioteca em grade, busca por nome, filtros por categoria e favoritos.
- Botão **Atualizar** para reconhecer jogos adicionados sem reiniciar o programa.
- Abertura segura do Flash Player, sem `shell=True`.
- Favoritos salvos no perfil do Windows, em `%APPDATA%\PlayOuro\favorites.json`.

## Estrutura organizada

```text
passatempo/
├── play.py                    # Launcher oficial
├── build.ps1                  # Gera a release portátil
├── flashplayer_32_sa.exe      # Player Flash standalone
├── JOGOS/                     # Biblioteca original de arquivos .swf
├── README.md
├── arquivos_antigos/          # Protótipos, builds e scripts antigos (ignorado pelo Git)
│   └── 2026-07-10/
├── build/                     # Arquivos temporários do PyInstaller (ignorado pelo Git)
└── release/                   # Versão pronta para uso (ignorado pelo Git)
    └── PlayOuro/
        ├── PlayOuro.exe
        ├── flashplayer_32_sa.exe
        ├── JOGOS/
        └── _internal/
```

As versões antigas (`play-new`, `dist`, especificações e scripts antigos) foram preservadas em `arquivos_antigos/2026-07-10/`. Elas não participam da versão atual.

## Como usar

### Pelo Python

Requisitos:

- Windows;
- Python com Tkinter/Tcl-Tk instalado;
- `flashplayer_32_sa.exe` e a pasta `JOGOS` ao lado de `play.py`.

Na pasta do projeto, execute:

```powershell
python play.py
```

### Abrir o executável para jogar

1. Abra a pasta `release\PlayOuro` no Explorador de Arquivos.
2. Dê dois cliques em `PlayOuro.exe`.
3. Na tela do Play Ouro, pesquise ou escolha um jogo na biblioteca.
4. Clique em **JOGAR ▶** no cartão do jogo escolhido.

```text
release\PlayOuro\PlayOuro.exe
```

O Flash Player abrirá o jogo em outra janela. Para fechar um jogo, feche essa janela normalmente e volte ao Play Ouro para escolher outro.

O executável, `flashplayer_32_sa.exe`, a pasta `JOGOS` e `_internal` precisam permanecer juntos. Não copie somente o `.exe`.

## Como organizar a biblioteca

1. Copie um novo arquivo `.swf` diretamente para `JOGOS`.
2. Abra o launcher ou clique em **Atualizar**.
3. Pesquise pelo nome, escolha uma categoria ou marque o jogo com uma estrela para adicioná-lo aos favoritos.

O título e a categoria exibidos são criados a partir do nome do arquivo; o arquivo original continua intacto.

Atalhos úteis:

- `Ctrl + F`: foca a busca;
- `Enter`: abre o primeiro resultado;
- `Esc`: limpa a busca.

## Gerar a release pelo script

Primeiro, confirme que o Python consegue iniciar o Tkinter:

```powershell
python -c "import tkinter as tk; root = tk.Tk(); root.withdraw(); root.update_idletasks(); root.destroy(); print('Tkinter OK')"
```

Instale o PyInstaller uma única vez:

```powershell
python -m pip install --user --upgrade pyinstaller
```

Depois execute o script. Se `python` já aponta para um Python com Tkinter, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Para informar um Python específico, por exemplo o Python 3.13 instalado no perfil do usuário:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -Python "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
```

O script verifica o Tkinter antes do build e gera uma pasta completa em `release\PlayOuro\`.

## Gerar manualmente, sem o script

Use estes comandos no PowerShell a partir da raiz do projeto. Troque o valor de `$python` se estiver usando outra instalação válida do Python.

```powershell
$python = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"

New-Item -ItemType Directory -Force .\release, .\build\release, .\build\spec | Out-Null

& $python -m PyInstaller `
  --noconfirm `
  --clean `
  --windowed `
  --onedir `
  --name PlayOuro `
  --distpath .\release `
  --workpath .\build\release `
  --specpath .\build\spec `
  .\play.py

Copy-Item -LiteralPath .\flashplayer_32_sa.exe `
  -Destination .\release\PlayOuro\flashplayer_32_sa.exe -Force

Copy-Item -LiteralPath .\JOGOS `
  -Destination .\release\PlayOuro\JOGOS -Recurse -Force
```

O resultado final estará em `release\PlayOuro\PlayOuro.exe`. O formato `--onedir` é intencional: o app depende do player e da biblioteca de jogos ao lado do executável.

## Solução de problemas

| Situação | Como resolver |
| --- | --- |
| O launcher não encontra o Flash Player | Deixe `flashplayer_32_sa.exe` na mesma pasta de `PlayOuro.exe` ou de `play.py`. |
| A pasta de jogos não foi encontrada | Deixe `JOGOS` ao lado do launcher, com esse mesmo nome. |
| Um jogo não aparece | Confirme que termina em `.swf`, está diretamente dentro de `JOGOS` e clique em **Atualizar**. |
| O build informa que o Tkinter não inicia | Use ou reinstale um Python com Tcl/Tk; o comando de teste desta documentação deve mostrar `Tkinter OK`. |
| O Windows exibe um aviso ao abrir a release | O executável gerado localmente não possui assinatura digital; use-o apenas se a origem dos arquivos for confiável. |

## Observações

- O Flash foi descontinuado nos navegadores; este projeto funciona com o player standalone local.
- Alguns arquivos `.swf` podem ter limitações próprias e não funcionar perfeitamente.
- Antes de redistribuir jogos, player ou uma release do projeto, confirme as licenças e permissões dos arquivos incluídos.
