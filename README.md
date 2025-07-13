# Calmind

## 🧠 O que é o Calmind?

O **Calmind** é uma extensão para o Google Chrome que usa **inteligência artificial** para tornar conteúdos da internet mais acessíveis a **pessoas neurodivergentes**.  
Nosso objetivo é transformar páginas com blocos extensos de texto em informações mais claras, organizadas e fáceis de ler.

Este repositório contém o backend responsável por **orquestrar as chamadas ao modelo Gemini**, que adapta o conteúdo original para um formato mais acessível.

---

## 💡 Por que criamos isso?

Muito se fala sobre **diversidade e inclusão** no mercado de trabalho, mas pouco se discute sobre **acessibilidade no aprendizado**.  
Como uma pessoa neurodivergente pode se capacitar se a maioria dos conteúdos online são difíceis de consumir?  
E quando ingressam em uma empresa, conseguem realmente entender os materiais de onboarding?
E essa extensão é expansível para *qualquer* tipo de conteúdo de texto.

O Calmind nasceu para **reduzir essas barreiras** e promover uma internet mais inclusiva.

---

## 🚀 Como usar

1. Instale o Python 3.13  

2. Instale as dependências com:  
   ```bash
   pip install -r requirements.txt
    ```
3. Execute o script:
   ```bash
   python main.py
    ```

## 🛠 Tecnologias utilizadas
* Python 3.13
* Gemini (Google GenAI)
* AsyncIO
* Docker
* Google Cloud Functions

## ☁️ Deploy na Nuvem
O serviço está publicado na Google Cloud Platform, utilizando Cloud Functions para escalar de forma eficiente e com baixo custo.

## 🔍 O que este serviço faz?
* O conteúdo da página que o usuário deseja ler é enviado pelo frontend.

* A primeira chamada à IA organiza esse conteúdo em "chunks" (blocos menores e mais fáceis de ler).

* A segunda etapa envolve uma nova chamada à IA para adaptar expressões, simplificar frases e tornar o texto mais compreensível para pessoas com diferentes perfis de cognição.