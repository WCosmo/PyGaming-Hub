# 🛡️ Disk Defrag

> "O servidor central entrou em colapso lógico. Você é o protocolo de defesa final encarregado de impedir a perda total de dados."

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-CE-green?style=for-the-badge&logo=pygame&logoColor=white)
![Status](https://img.shields.io/badge/Status-Finalizado-success?style=for-the-badge)

## 📋 Sobre o Projeto

**Disk Defrag** é um jogo de simulação de manutenção de sistemas desenvolvido inteiramente em **Python** utilizando a biblioteca **Pygame**. 

O projeto foi concebido sob restrições técnicas rigorosas para demonstrar domínio de lógica de programação:
* 🚫 **Zero Sprites:** Todos os gráficos (cursor, inimigos, partículas) são renderizados em tempo real via `pygame.draw`.
* ⚙️ **Configuração Externa:** Todo o mapeamento de teclas e resolução é lido de um arquivo `conf.ini`.
* 💾 **Persistência de Dados:** Sistema de *Highscores* local (`system.log`).

---

## 🎮 Mecânicas e Features

O jogo simula um cursor de leitura/gravação em um Disco Rígido sob ataque de fragmentação e malwares.

| Elemento | Tipo | Comportamento |
| :--- | :--- | :--- |
| 🟩 **Verde** | **Cursor** | Você. Navegue pela grade para reparar setores. |
| 🟥 **Vermelho** | **Bad Block** | Setor danificado. Repare para ganhar pontos. |
| 🟪 **Roxo** | **Rootkit** | **Bomba Lógica.** Explode em 2.5s destruindo setores vizinhos. Prioridade máxima! |
| 🟦 **Azul** | **Shield** | **Buff.** Protege contra o próximo erro ou dano. |
| ⬜ **Cinza** | **Lock** | **Debuff (Ransomware).** Congela seus controles por 2s se tocado. |
| 🟦 **Ciano** | **NUKE** | **Ultimate.** Limpa toda a tela. Liberado ao atingir **Combo 50x**. |

### ⚡ Sistema de Combo
Acertar setores rapidamente sem errar aumenta seu multiplicador (até **10x**). Manter o ritmo é essencial para bater o recorde do sistema.

---

## ⌨️ Controles

Os controles são configuráveis via `conf/conf.ini`, mas o padrão definido é:

| Ação | Tecla Padrão | Função |
| :--- | :---: | :--- |
| **Navegação** | `W` `A` `S` `D` | Move o cursor pela matriz do HD. |
| **Ação A** | `O` | **Reparar / Confirmar.** Usa no menu e no jogo. |
| **Ação B** | `P` | **Pause / Resume.** Congela o sistema temporariamente. |
| **Hard Exit** | `Enter` | Encerra a execução imediatamente (BSOD ou Jogo). |

---

## 🚀 Instalação e Execução

Pré-requisitos: Python 3.10+ instalado.

```bash
# 1. Clone o repositório
git clone [https://github.com/SEU-USUARIO/PyGaming-Hub.git](https://github.com/SEU-USUARIO/PyGaming-Hub.git)

# 2. Entre na pasta do projeto
cd PyGaming-Hub

# 3. Instale as dependências
pip install pygame

# 4. Execute o jogo
python games/DiskDefrag/main.py