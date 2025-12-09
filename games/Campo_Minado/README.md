
#🧨 Campo Minado – PyGaming Hub

Versão simples do jogo **Campo Minado**
---

## 📌 1. Visão Geral

O jogo usa teclado pra tudo e carrega automaticamente:

* tamanho da tela
* fullscreen opcional
* teclas configuráveis
* cursor para navegar nas células
* lógica completa (minas, números, bandeiras, flood-fill, vitória/derrota)

A qualquer momento você pode apertar **Pause** pra fechar o jogo.

---

## ⚙️ 2. Configuração (conf.ini)

O sistema procura:

```
conf/conf.ini
../conf/conf.ini
```

Se existir, o jogo lê:

### **[Display]**

* `width` – largura
* `height` – altura
* `fullscreen` – true/false

### **[Controls]**

* `up`, `down`, `left`, `right`
* `action_a` → revelar
* `action_b` → bandeira / reiniciar
* `pause`

Se faltar algo, o padrão é usado.
A função `name_to_keycode()` converte texto tipo `"z"` ou `"up"` para teclas do pygame.

---

## 🖥️ 3. Inicialização

O jogo prepara:

* janela com tamanho desejado
* fullscreen (opcional)
* clock de FPS
* fontes padrão

Ex.:

```python
screen = pygame.display.set_mode((W, H), flags)
```

---

## 🎯 4. Regras do Jogo

* Grade: **9x9**
* Minas: **10**
* Células ajustam tamanho automático
* Tabuleiro fica centralizado
* Todas as cores e estilos são definidos no código

---

## 🧠 5. Estrutura dos Dados

O tabuleiro usa três matrizes:

| Matriz     | Função                   |
| ---------- | ------------------------ |
| `board`    | -1 = mina / 0–8 = número |
| `revealed` | células já abertas       |
| `flagged`  | células marcadas         |

A função `new_board()` cria tudo:

* sorteia minas
* calcula números
* monta matrizes auxiliares

---

## 🏳️ 6. Lógica Principal

* **reveal_cell**

  * mina → derrota
  * zero → abre área com flood-fill
  * número → só mostra
* **bandeira**
  funciona só em célula não revelada
* **check_win**
  confere se todas as células seguras foram abertas
* **reset_game**
  reinicia tudo

---

## 🎨 7. Renderização (pygame.draw)

Sem imagens, só shapes:

* `draw_board()` → tabuleiro, números, minas, bandeiras, cursor
* `draw_status()` → textos de ajuda, minas restantes, vitória/derrota

---

## 🎮 8. Loop Principal

A cada frame o jogo:

1. limita a 60 FPS
2. lê eventos
3. move cursor
4. revela célula (A)
5. marca bandeira (B)
6. checa vitória/derrota
7. redesenha tela se precisar

Sai com **Pause** ou fechando a janela.

---

## ⌨️ 9. Controles (padrão)

| Ação                 | Tecla      |
| -------------------- | ---------- |
| Mover                | Setas      |
| Revelar              | **Z**      |
| Bandeira / Reiniciar | **X**      |
| Sair                 | **Escape** |

Todos podem ser mudados no `conf.ini`.

---

## 🧱 10. Estrutura do Código

```
main.py
├── leitura do conf.ini
├── setup inicial
├── funções do tabuleiro
│   ├── new_board
│   ├── reveal_cell
│   └── check_win
├── funções de desenho
│   ├── draw_board
│   └── draw_status
└── main()
```

---

## 🔧 Configuração 
Todas as configurações do console e dos jogos são controladas pelo arquivo `conf/conf.ini`: 
* `[Display]`: `width`, `height`, `fullscreen`. 
* `[Controls]`: `up`, `down`, `left`, `right`, `action_a`, `action_b`, `pause`. 
* `[Info]`: `authors` (o autor do console). --- 

## ✍️ Créditos 
* **Autor do Console (PyGaming Hub):** Wilson Cosmo
* **Autores dos Jogos:** Madson Santos e Sebastião
## 📄 Licença 
Este projeto está sob a licença GNU. Veja o arquivo `LICENSE` para mais detalhes.
