# Reflexo Quântico

Jogo educacional para o PyGaming Hub focado em tempo de reação e correspondência de cores. Todo o desenho é feito com primitivas do Pygame.

## Objetivo e mecânica
- Você é um quadrado branco de 40x40 px.
- A cada rodada, uma cor-alvo é exibida no topo (nome + amostra).
- Portais coloridos (círculos) surgem aleatoriamente nas bordas. Colida com o portal da cor-alvo antes do tempo da rodada acabar.
- Acerto: +1 ponto e nova cor-alvo. Erro ou tempo estourado: -1 ponto e registra 1 erro.
- O jogo termina ao alcançar 3 erros ou 30s totais de partida.

## Controles (lidos de `conf/conf.ini` na raiz do Hub)
Por padrão (já definido no `conf/conf.ini` do projeto):
- Movimento: `w`, `a`, `s`, `d`
- Boost: `o` (action_a) — aumenta a velocidade
- Foco: `p` (action_b) — movimento mais preciso
- Pause: `enter` (pause) — primeiro toque pausa, segundo toque sai para o hub; `o` retoma
- Música: `musica.mp3` na pasta do jogo (reproduzida em loop, sem uso de imagens).

### Fluxo de telas
- Tela inicial: mostra instruções. `o` inicia a partida. `p` fecha o jogo (volta ao Hub).
- Partida: `enter` (pause) pausa; um segundo `enter` na pausa encerra e volta ao Hub; `o` durante a pausa retoma.
- Tela final: aparece ao fim do tempo ou 3 erros. `o` joga novamente. `enter` (Pause) volta ao Hub.

## Configuração
O jogo lê resolução, fullscreen e mapeamento de teclas do arquivo `conf/conf.ini` na raiz do PyGaming Hub. Exemplo:
```
[Display]
width = 1280
height = 720
fullscreen = False

[Controls]
up = w
down = s
left = a
right = d
action_a = o
action_b = p
pause = enter
```
Use `pygame.key.key_code()` compatível: valores como `enter`, `escape`, `space`, letras e setas.

## Como executar
- Pelo Hub: selecione “Reflexo Quântico” na lista de jogos. A tela inicial aparecerá; pressione `o` para começar.
- Direto pelo Python (na raiz do Hub): `python games/ReflexoQuântico/main.py`

## Estado do projeto
- Regras implementadas conforme guia oficial do PyGaming Hub.
- Apenas primitivas de desenho do Pygame.
- Pausa congela os temporizadores de rodada e partida.

## Estrutura
- `main.py` — jogo completo e loop principal.
- `data.inf` — metadados exigidos pelo Hub.
- `musica.mp3` — música usada no jogo.

## Solução de problemas
- **Jogo fecha ao iniciar**: confirme que `conf/conf.ini` existe na raiz do Hub com as seções `Display` e `Controls`.
- **Tecla não funciona**: verifique se o nome no `conf.ini` é aceito pelo `pygame.key.key_code` (ex.: `return`/`enter`, `escape`, `w`, `a`, etc.).
- **Resolução errada**: ajuste `width`/`height` em `conf/conf.ini` e reinicie o jogo.
