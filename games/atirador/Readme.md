# 🚀 Jogo do Atirador Espacial

## 1. Visão Geral e Conceito do Jogo

O **"Jogo do Atirador Espacial"** é um jogo de tiro vertical desenvolvido para o console PyGaming Hub. O objetivo é sobreviver a 5 fases de 50 segundos, gerenciando a coleta de power-ups e evitando que inimigos comuns passem pela linha de defesa.

### Autores
João Pedro Muniz, Daniel Harrison, Thalita Azevedo

---

## 2. Sistema de Fases e Dificuldade

O jogo é dividido em 5 fases cronometradas (50 segundos por fase).

* **Progressão:** Ao completar 50 segundos sem perder todas as vidas, o jogador avança de fase.
* **Dificuldade:** A cada nova fase, a **velocidade de queda** dos inimigos aumenta em +0.5 pontos e o *tempo de spawn* diminui, aumentando a intensidade do desafio.
* **Vidas Visuais:** A contagem de "Erros" é representada visualmente por **três corações** no canto superior direito.

---

## 3. Inimigos e Power-Ups (Mecânicas Detalhadas)

O sistema de entidades é dividido entre inimigos de pontuação (que causam erro se perdidos) e power-ups (que desaparecem sem penalidade).

### A. Inimigos de Pontuação (Causam Erro)

| Entidade | Forma Geométrica | Valor | Lógica |
| :--- | :--- | :--- | :--- |
| **Básico** | Quadrado, Círculo | 10 pts | Padrão mais comum (60% de chance de spawn). Causam 1 Erro se passarem. |
| **Especial (Hexágono)** | Hexágono | 25 pts | Inimigo de alto valor. Se move mais lentamente para compensar a dificuldade de acerto. Causa 1 Erro se perdido. |

### B. Power-Ups e Bônus (Não Causam Erro)

| Power-Up | Forma | Duração | Efeito e Cor |
| :--- | :--- | :--- | :--- |
| **Velocidade** | Estrela (Ouro) | 7s | Aumenta a velocidade de movimento da nave em 50%. (Chance de 10% de spawn). |
| **Tiro Triplo** | Diamante (Vermelho) | 10s | O disparo é triplicado. |
| **Slow-Motion** | Retângulo Arredondado (Azul) | 10s | Reduz a velocidade de queda de *todos* os inimigos pela metade. |

---

## 4. Instruções de Jogo

* **Mover:** Tecla configurada em `LEFT` ou `RIGHT`.
* **Disparo:** Automático
* **Pause:** Tecla definida no `conf.ini`. No menu de Game Over/Vitória, use o mouse para **Jogar Novamente** ou **Sair**.