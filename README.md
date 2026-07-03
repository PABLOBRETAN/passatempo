# Passatempo - Jogos antigos da internet

Colecao local de jogos antigos em Flash (`.swf`) com um menu simples feito em Python. O projeto foi pensado para abrir os jogos sem depender do navegador, usando o Flash Player standalone que fica junto dos arquivos.

## O que tem no projeto

- `play.py`: programa principal. Ele cria uma janela com a lista dos jogos e abre o jogo escolhido.
- `JOGOS/`: pasta com os arquivos `.swf`.
- `flashplayer_32_sa.exe`: Flash Player standalone usado para executar os jogos.
- `dist/play.exe`: versao executavel ja gerada do menu.
- `dist/JOGOS/`: copia dos jogos para acompanhar o executavel.
- `dist/flashplayer_32_sa.exe`: copia do Flash Player para acompanhar o executavel.
- `gerar exe.txt`: comando usado para gerar o executavel com PyInstaller.
- `instal py.ps1`: comando basico para instalar o PyInstaller.
- `play.spec`: configuracao gerada pelo PyInstaller.

## Como usar

### Opcao 1: abrir pelo executavel

1. Entre na pasta `dist`.
2. Abra `play.exe`.
3. Escolha um jogo na lista.

Importante: para funcionar, o `play.exe`, o `flashplayer_32_sa.exe` e a pasta `JOGOS` precisam ficar juntos na mesma pasta.

### Opcao 2: abrir pelo Python

Requisitos:

- Windows.
- Python instalado.
- `flashplayer_32_sa.exe` na mesma pasta do `play.py`.
- Pasta `JOGOS` na mesma pasta do `play.py`.

Comando:

```powershell
python play.py
```

## Como adicionar novos jogos

1. Coloque o arquivo `.swf` dentro da pasta `JOGOS`.
2. Abra novamente o programa.
3. O jogo novo aparecera automaticamente na lista.

O nome exibido no menu e o nome do arquivo sem a extensao `.swf`. Para deixar o menu mais organizado, renomeie o arquivo antes de colocar na pasta.

## Como gerar um novo executavel

Instale o PyInstaller:

```powershell
pip install pyinstaller
```

Depois gere o executavel:

```powershell
pyinstaller --windowed --onefile play.py
```

O arquivo gerado fica em:

```text
dist/play.exe
```

Depois de gerar, copie para a pasta `dist`:

- `flashplayer_32_sa.exe`
- a pasta `JOGOS`

Sem esses arquivos ao lado do `play.exe`, o menu abre erro porque nao encontra o player ou os jogos.

## Como funciona

O programa identifica a pasta onde esta sendo executado. A partir dela, procura:

- `flashplayer_32_sa.exe`
- `JOGOS/`

Depois lista todos os arquivos com extensao `.swf`, cria um botao para cada jogo e, quando um botao e clicado, abre o Flash Player passando o caminho do jogo escolhido.

## Organizacao sugerida

```text
passatempo/
|-- play.py
|-- flashplayer_32_sa.exe
|-- JOGOS/
|   |-- Pac man.swf
|   |-- SONIC.swf
|   `-- outros jogos...
`-- dist/
    |-- play.exe
    |-- flashplayer_32_sa.exe
    `-- JOGOS/
```

## Observacoes

- Flash e uma tecnologia antiga e foi descontinuada nos navegadores modernos. Este projeto usa o player standalone para preservar e abrir os jogos localmente.
- Alguns jogos podem nao funcionar perfeitamente dependendo do arquivo `.swf`.
- Evite apagar ou mover `flashplayer_32_sa.exe` e `JOGOS`, porque o menu depende desses caminhos.
- Se o Windows bloquear o executavel baixado ou copiado, pode ser necessario liberar o arquivo nas propriedades do Windows.

## Ideias futuras

- Adicionar busca por nome do jogo.
- Separar jogos por categoria.
- Mostrar capas ou miniaturas.
- Criar botao de favoritos.
- Corrigir textos com acentos e emojis caso aparecam caracteres estranhos em algum computador.
