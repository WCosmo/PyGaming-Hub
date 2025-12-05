# PyGaming Hub 🎮 

Um launcher de jogos educacionais feitos em Python, desenvolvido com a biblioteca Pygame. Este projeto funciona como um *frontend* (interface) de console arcade, projetado para descobrir e lançar outros jogos em Pygame de forma organizada.  

## 🎯 Sobre o Projeto O **PyGaming Hub** foi criado com um duplo objetivo: 
1. **Como Produto:** Servir como um hub centralizado e simples para organizar e jogar pequenos jogos educacionais feitos em Python/Pygame. É ideal para *game jams*, oficinas de programação ou para agrupar projetos de uma turma.
2. **Como Estudo:** Ser um projeto prático que demonstra conceitos importantes de desenvolvimento de software em Python, como:
* Gerenciamento de "estados" (telas) em Pygame (menu, ajuda, biblioteca, etc.).
* Leitura e escrita de arquivos de configuração externos (`.ini`).
* Detecção dinâmica de conteúdo (varredura de pastas de jogos).
* Execução de scripts Python externos como subprocessos. 

## ✨ Funcionalidades 
* **Menu Principal Navegável:** Interface limpa para acessar as diferentes seções do console.
* **Detecção Automática de Jogos:** Escaneia o diretório `/games` e lista automaticamente qualquer jogo que contenha os arquivos `main.py` e `data.inf`.
* **Configuração Centralizada:** Todas as configurações (resolução, tela cheia e controles) são salvas em `conf/conf.ini`.
* **Controles Unificados:** Os jogos lançados são projetados para ler o mesmo `conf/conf.ini`, permitindo que o usuário configure seus controles **uma única vez** no menu principal.
* **Lançador de Subprocessos:** Inicia os jogos de forma independente e, quando o jogo é fechado (com a tecla "Pause"), retorna automaticamente ao menu do Hub. 

## 🕹️ Como Adicionar Seus Próprios Jogos 

Para que o PyGaming Hub detecte seu jogo educacional, basta seguir esta estrutura de pastas: 
```
PyGaming Hub/
├── games/
│   └── MeuNovoJogo/       <-- 1. Crie uma pasta para seu jogo
│       ├── main.py        <-- 2. O script principal do seu jogo
│       └── data.inf       <-- 3. O arquivo de metadados
├── conf/
└── main.py                <-- O launcher principal
``` 

O arquivo `data.inf` é essencial e deve ter o seguinte formato: 
```
[Game]
nome = Nome de Exibição do Jogo
autores = Nome do Autor 1, Autor 2 
``` 

O script `main.py` do seu jogo (como o "Simple Mover" de exemplo) deve ser capaz de ler o arquivo `conf/conf.ini` da raiz do projeto para carregar as configurações de controle e resolução. 

## 🚀 Como Executar 
Você precisará do Python 3 e da biblioteca Pygame instalados. 
1. **Clone este repositório:**
```
git clone https://github.com/seu-usuario/pygaming-hub.git
cd pygaming-hub
```
2. **(Opcional) Crie um ambiente virtual:**
```
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```
3. **Instale as dependências:**
```
pip install pygame
```
5. **Execute o console:**
```
python main.py
```
Na primeira execução, a pasta `conf/` e o arquivo `conf.ini` com as configurações padrão serão criados automaticamente.  

## 🔧 Configuração 
Todas as configurações do console e dos jogos são controladas pelo arquivo `conf/conf.ini`: 
* `[Display]`: `width`, `height`, `fullscreen`. 
* `[Controls]`: `up`, `down`, `left`, `right`, `action_a`, `action_b`, `pause`. 
* `[Info]`: `authors` (o autor do console). --- 

## ✍️ Créditos 
* **Autor do Console (PyGaming Hub):** Wilson Cosmo
* **Autores dos Jogos:** Os créditos de cada jogo são carregados dinamicamente a partir dos seus respectivos arquivos `data.inf` e são exibidos na tela "Sobre" do console. 

## 📄 Licença 
Este projeto está sob a licença GNU. Veja o arquivo `LICENSE` para mais detalhes.
