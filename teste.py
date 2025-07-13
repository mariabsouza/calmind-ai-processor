import os
import asyncio
import json
import re
from dotenv import load_dotenv
from flask import jsonify
import functions_framework
from google import genai
from google.genai import types
from models.FinalOutput import OptimizedChunkContent, OptimizedContent

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
CHUNK_OBJECT_REGEX = re.compile(r'\{[^{}]+\}(?=,|\])')  # captura objetos JSON simples

# Task assíncrona para reescrever um chunk
async def process_chunk_async(chunk_dict):
    from prompts.rewriter_agent import rewriter_agent_prompt

    config = types.GenerateContentConfig(
        temperature=0.4,
        response_schema=OptimizedChunkContent,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="application/json"
    )

    response = await asyncio.to_thread(
        lambda: client.models.generate_content(
            model="gemini-2.5-flash",
            contents=rewriter_agent_prompt(chunk_dict["chunk_content"]),
            config=config
        )
    )

    return response.parsed

@functions_framework.http
def function_handler(request):
    data = request.get_json(silent=True)
    original_content = data.get("content", "Texto padrão")

    stream_config = types.GenerateContentConfig(
        temperature=0.2,
        response_schema=None,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        response_mime_type="application/json"
    )

    buffer = ""
    seen_chunks = set()
    rewriter_tasks = []
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def handle_stream():
        nonlocal buffer

        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [original_content]}],
            config=stream_config
        ):
            if not chunk.text:
                continue

            buffer += chunk.text

            # Só processa se o array de chunks já começou
            if '"original_chunks":[' in buffer:
                start = buffer.find('"original_chunks":[') + len('"original_chunks":[')
                array_buffer = buffer[start:]

                for match in CHUNK_OBJECT_REGEX.finditer(array_buffer):
                    chunk_str = match.group()
                    try:
                        chunk_dict = json.loads(chunk_str)
                        chunk_id = chunk_dict.get("chunk_title") + chunk_dict.get("chunk_content")[:30]
                        if chunk_id not in seen_chunks:
                            seen_chunks.add(chunk_id)
                            # dispara task e armazena para depois aguardar
                            task = loop.create_task(process_chunk_async(chunk_dict))
                            rewriter_tasks.append(task)
                    except json.JSONDecodeError:
                        continue

        # espera todas as rewriter tasks paralelas
        rewritten_chunks = await asyncio.gather(*rewriter_tasks, return_exceptions=False)
        return rewritten_chunks

    rewritten_chunks = loop.run_until_complete(handle_stream())

    # Tenta montar resultado final com título e chunks originais
    try:
        parsed_json = json.loads(buffer[buffer.find("{"):])
        title = parsed_json.get("content_title", "")
        subtitle = parsed_json.get("content_subtitle")
        original_chunks = parsed_json.get("original_chunks", [])
    except Exception as e:
        print("Erro final ao parsear:", e)
        title = "Sem título"
        subtitle = None
        original_chunks = []

    final = OptimizedContent(
        content_title=title,
        content_subtitle=subtitle,
        original_chunks=original_chunks,
        replaced_chunks=rewritten_chunks
    )

    return jsonify(final.model_dump()), 200, {"Access-Control-Allow-Origin": "*"}



data = {
    "content": "<div id=\"readability-page-1\" class=\"page\"><div data-framer-name=\"Content\" id=\"1\" data-framer-component-type=\"RichTextContainer\" data-border=\"true\"><p>Produzir um <strong>Trabalho de Conclusão de Curso (TCC)</strong> sempre exige dedicação, mas a jornada costuma ser repleta de tarefas repetitivas: encontrar boas referências, estruturar capítulos, organizar metodologias e, claro, manter tudo formatado em conformidade com normas acadêmicas.&nbsp;</p><p>Hoje, graças aos avanços em Inteligência Artificial (IA), boa parte desse processo pode ser otimizado. Isso inclui desde a escolha do tema até a revisão final. No entanto, o uso de<strong> IA para TCC </strong>pede responsabilidade e domínio de algumas estratégias para que o resultado seja realmente acadêmico, autoral e confiável.</p><p>Neste conteúdo, exploraremos<strong> formas de incluir a IA de modo seguro em cada etapa do TCC</strong>, além de apresentar <strong>diferentes ferramentas</strong>, desde sugestões de estrutura textual até buscas bibliográficas otimizadas.&nbsp;</p><h2>IA para TCC: Como usar inteligência artificial para fazer monografias?</h2><p>A aplicação de IA em trabalhos acadêmicos avança a passos largos. Ferramentas que, inicialmente, eram vistas com desconfiança, hoje já se tornaram companheiras constantes, auxiliando na formatação de normas técnicas e na construção de fundamentações teóricas. Ao mesmo tempo, alguns estudantes ainda se questionam se <strong>é correto ou não recorrer a esses recursos para “acelerar” o TCC</strong>.</p><p>O ideal é perceber que <strong>a IA não substitui a capacidade de raciocínio crítico e a pesquisa cuidadosa</strong>. Em vez disso, ela atua como uma aliada para lidar com tarefas que tomam tempo, como <strong>ajustar referências ou sugerir novas bibliografias</strong>.&nbsp;</p><p>Com esse tipo de auxílio, o(a) aluno(a) fica livre para se dedicar ao que realmente importa: aprofundar-se no conteúdo, argumentar e construir um texto de valor para a comunidade acadêmica. Assim, a ideia é evoluir de forma adaptável, aproveitando as facilidades tecnológicas sem sacrificar o rigor metodológico.</p><p>Por exemplo, se você decide implementar um estudo de caso sobre marketing digital e deseja encontrar referências científicas, há IAs que fazem buscas rápidas em bases confiáveis, retornando sugestões de artigos revisados por pares. A partir daí, você pode focar a leitura no que traz embasamento real ao seu texto.&nbsp;</p><p>Caso fique travado na escrita de um capítulo, <strong>modelos de IA também podem sugerir uma estrutura inicial</strong>, que você revisa e adapta para o tom desejado. Tudo isso <strong>diminui o tempo perdido em tarefas operacionais</strong>, direcionando sua energia para o que realmente importa na pesquisa.</p><h2>É permitido usar IA no TCC?</h2><p>A dúvida sobre <strong>“poder ou não” usar IA no TCC</strong> é frequente. A verdade é que <strong>não existe, em âmbito nacional, uma legislação </strong>única que trate do assunto. Normalmente, cada instituição de ensino cria suas próprias regras, detalhando quando e como as ferramentas de IA podem ser utilizadas.&nbsp;</p><p>Portanto, se você pretende recorrer a esses recursos, o primeiro passo é <strong>conferir as normas internas da faculdade ou da universidade</strong>. Em muitos casos, o uso é bem-vindo, desde que haja<strong> transparência</strong>.&nbsp;</p><p>Isso implica citar, dentro do trabalho, como a IA contribuiu: seja fornecendo sugestões de escrita, apoiando em revisões textuais ou indicando bibliografias. A honestidade é um princípio básico da academia.&nbsp;</p><p>Quem a pratica, na maioria das vezes, só tem a ganhar, demonstrando maturidade e dominando as práticas de adaptação às inovações tecnológicas.Convém também alinhar o uso da IA com seu orientador.&nbsp;</p><p>Se a instituição entende esse recurso como uma extensão do seu trabalho, em vez de sua substituição, a conversa tende a ser bem positiva. Afinal, todos apreciam a eficiência, principalmente quando ela está aliada à confiabilidade.&nbsp;</p><p><strong>O fundamental é não perder de vista a produção autoral:</strong> você continua sendo responsável pelas ideias centrais, interpretações dos resultados e originalidade dos argumentos.</p><h2>Em quais etapas do TCC a IA pode ajudar?</h2><p>A produção de uma monografia segue, em geral, um<strong> roteiro básico:</strong> escolher o tema, delimitar o problema de pesquisa, revisar a literatura, fazer a parte metodológica, analisar os dados e encerrar com conclusões. Em <strong>cada uma dessas fases, as IAs conseguem contribuir de forma diferente</strong>. Abaixo, apresentamos alguns exemplos práticos:</p><ul><li data-preset-tag=\"p\"><p><strong>Escolha e delimitação de tema:&nbsp;</strong></p></li></ul><p>Ferramentas de IA podem ser úteis em brainstormings iniciais. Você insere um tópico principal — por exemplo, “educação híbrida” — e<strong> recebe sugestões para recortes específicos</strong>, como “educação híbrida na formação de professores de Matemática” ou “estratégias de engajamento virtual em salas de aula híbridas”.</p><ul><li data-preset-tag=\"p\"><p><strong>Pesquisa bibliográfica:&nbsp;&nbsp;&nbsp;</strong></p></li></ul><p>Alguns modelos<strong> rastreiam artigos em bases científicas </strong>e retornam, em poucos segundos, estudos correlatos. Isso acelera a revisão de literatura, indicando fontes confiáveis. Ainda assim,<strong> é essencial conferir cada referência</strong>, validando se realmente existe e se se encaixa no escopo do seu trabalho.</p><ul><li data-preset-tag=\"p\"><p><strong>Estruturação do texto:&nbsp;&nbsp;&nbsp;</strong></p></li></ul><p>Quando surge aquela dificuldade de<strong> organizar ideias e capítulos</strong>, a IA pode apontar caminhos lógicos, sugerindo subtítulos ou blocos que facilitem a fluidez. É como ter alguém ao lado dizendo: “Que tal iniciar com esse conceito e depois explorar aquela metodologia?”</p><ul><li data-preset-tag=\"p\"><p><strong>Revisão ortográfica e de coesão:&nbsp;&nbsp;&nbsp;</strong></p></li></ul><p>Várias IAs funcionam como <strong>assistentes de gramática e estilo</strong>, detectando repetições, erros de concordância e falhas de pontuação. Isso otimiza seu fluxo de trabalho, deixando o texto mais claro e profissional.</p><p>Para não se perder nessas facilidades, lembre-se de que a IA, em última instância, não se responsabiliza pelos resultados. Quem garante a integridade e a solidez dos argumentos é você. Verificar, adaptar e conferir coerência são etapas indispensáveis antes de assinar a versão final.</p><h2>Qual a melhor IA para fazer um TCC?</h2><p>O mercado de IA oferece diversas soluções, cada uma com suas vantagens e restrições.<strong> A escolha depende dos objetivos</strong> e da etapa em que você está no TCC.&nbsp;</p><p>A seguir, conheça algumas das ferramentas mais citadas entre estudantes e pesquisadores. Lembre-se, porém, de que nenhuma plataforma substitui a análise crítica e a escrita autoral do estudante.</p><h3>Grammarly</h3><p><strong>Para quem escreve em inglês ou quer refinar traduções</strong>, o Grammarly é o queridinho de muitos usuários. Ele aponta erros de ortografia, sugere substituições de palavras redundantes e ajuda a padronizar o estilo.&nbsp;</p><p>O foco se mantém no idioma inglês, mas mesmo em textos em português algumas funcionalidades básicas podem ser úteis. Já a versão paga entrega <strong>recursos mais avançados de consistência textual</strong>.</p><p>No entanto, se o seu TCC for majoritariamente em português, é bom complementar com revisões humanas ou outras ferramentas mais adaptadas ao contexto brasileiro.</p><h3>Mettzer</h3><p>O Mettzer, especialmente popular entre estudantes brasileiros, se concentra em<strong> automatizar partes da formatação pela ABNT </strong>(Associação Brasileira de Normas Técnicas). Ele <strong>colabora na criação de referências, citações diretas e indiretas, e inclusive na diagramação</strong>.&nbsp;</p><p>Por mais que simplifique o processo, não ignore a leitura atenta das regras da sua instituição: às vezes há exigências adicionais. Ainda assim, para quem sente dificuldade com formatação, é um alívio contar com a rapidez oferecida pelo Mettzer.</p><h3>Research Rabbit</h3><p>O Research Rabbit funciona como um <strong>“mapeador” de referências</strong>. Ao digitar determinada palavra-chave, ele se encarrega de detectar artigos relacionados, construindo conexões entre temas. Se você está em busca de estudos complementares ou quer compreender novas perspectivas na sua revisão teórica, essa ferramenta se mostra bem valiosa.&nbsp;</p><p>A palavra-chave aqui é <strong>“organização”</strong>: ele facilita a vida de quem precisa juntar muitos artigos e analisar pontos em comum, principalmente em áreas com grande volume de produção acadêmica.</p><h3>Consensus</h3><p>O Consensus se propõe a fazer buscas em publicações revisadas por pares, oferecendo <strong>respostas embasadas em evidências científicas</strong>. Em vez de listar centenas de artigos, ele tenta apontar, de forma mais direta, se há respaldo ou não para determinada afirmação.&nbsp;</p><p>Isso pode ser bastante útil quando se quer reforçar um argumento, pois você rapidamente identifica titulares de pesquisas que confirmam (ou contrariam) uma ideia específica. Porém, nem sempre a ferramenta cobre todas as áreas do conhecimento com profundidade, cabendo verificar se há literatura suficiente na sua temática.</p><h3>Perplexity</h3><p>Essa ferramenta<strong> fornece explicações rápidas, citando as fontes consultadas</strong>. É útil para esclarecer dúvidas pontuais, como conceitos teóricos ou definições. Contudo, se o assunto do seu TCC for muito específico ou estiver em língua portuguesa, pode acontecer de a ferramenta não retornar resultados adequados. Mesmo assim, sua habilidade de mostrar referências originais <strong>poupa tempo na checagem de credibilidade</strong>.</p><h3>Gemini</h3><p>Desenvolvido pelo Google, é uma ferramenta versátil projetada para auxiliar em diversas tarefas, incluindo a <strong>redação de pesquisas</strong>. A ideia dele é processar linguagens naturais de forma ágil, auxiliando principalmente quem lida com grandes blocos de texto.&nbsp;</p><h3>ChatGPT</h3><p>O Chat GPT tem chamado atenção pela capacidade de produzir respostas coerentes em diversos idiomas. Ele pode<strong> sugerir estruturas de texto</strong>, gerar exemplos de introdução, revisar gramática, e é <strong>capaz de lidar com perguntas contextuais</strong> (quando você quer comparar conceitos ou elaborar breves análises).&nbsp;</p><p>Todavia, <strong>é essencial verificar as referências que ele menciona</strong>, pois em algumas situações os dados podem estar desatualizados ou serem fruto de “alucinações” do modelo. Use-o como uma base inicial; depois, refine as informações por conta própria.</p><h3>Paraphrase Tool</h3><p><strong>Para evitar repetições ou se livrar do famoso “bloqueio criativo” </strong>ao reescrever um parágrafo, há ferramentas de paráfrase que mudam a estrutura das frases, mantendo o sentido geral. Isso pode ser um auxílio considerável na hora de variar o vocabulário.&nbsp;</p><p>Entretanto, fique atento(a) ao risco de<strong> cair em plágio involuntário</strong> ou perder precisão terminológica. Sempre revise se o resultado ainda é pertinente e fiel ao que o trabalho acadêmico demanda.</p><h3>Quais cuidados e questões éticas ao usar IA no seu TCC?</h3><p>A empolgação ao descobrir essas ferramentas pode levar ao uso desmedido. Vale, portanto, observar alguns cuidados fundamentais:</p><ul><li data-preset-tag=\"p\"><p><strong>Verificação das referências: </strong>Muitas IAs podem citar estudos que não existem ou bibliografias equivocadas. Antes de listar algo no seu referencial, confira a validade.</p></li><li data-preset-tag=\"p\"><p><strong>Autonomia do(a) aluno(a):</strong>&nbsp; Não delegue o desenvolvimento completo ao software. A capacidade de análise, reflexão e autoria permanece sendo sua.</p></li><li data-preset-tag=\"p\"><p><strong>Citações adequadas:</strong> Se você parafraseia ou adapta textos de outros autores, mantenha as devidas citações para não ferir normas de plágio.</p></li><li data-preset-tag=\"p\"><p><strong>Políticas da instituição:</strong> Seja transparente. Às vezes, a universidade exige declaração formal sobre o uso de IA. É sempre melhor alinhar essa prática com seu orientador.</p></li></ul><h2>Dicas para usar IA no TCC</h2><p>Para realmente aproveitar o potencial da IA e manter a qualidade do seu trabalho, algumas recomendações fazem toda a diferença:</p><ol><li data-preset-tag=\"p\"><p><strong>Encontre referências, mas leia os originais&nbsp;&nbsp;</strong></p></li></ol><p>A IA pode sugerir artigos e livros. No entanto, jamais inclua citações de fontes que você não tenha checado pessoalmente. Essa verificação assegura que o conteúdo esteja alinhado ao que você precisa e evita erros futuros.</p><ol start=\"2\"><li data-preset-tag=\"p\"><p><strong>Aproveite a formatação, porém revise&nbsp;&nbsp;</strong></p></li></ol><p>Ferramentas como o Mettzer ajudam na formatação ABNT, mas há variações conforme a instituição. Faça uma checagem manual para confirmar se detalhes como margens, paginação e sumário estão de acordo com as exigências locais.</p><ol start=\"3\"><li data-preset-tag=\"p\"><p><strong>Use a IA como consultora, não como autora&nbsp;&nbsp;</strong></p></li></ol><p>Permita que ela aponte estruturas, verifique ortografia e ofereça brainstorming de ideias. Entretanto, a conclusão, o desenvolvimento do raciocínio e a defesa das hipóteses devem ser seus, mantendo a essência crítica característica de um TCC.</p><p><a href=\"https://adapta.org/\" rel=\"noopener\">A Inteligência Artificial </a>abre portas para tornar o desenvolvimento de um TCC mais produtivo, pontual e livre de erros mecânicos.&nbsp;</p><p>Contudo, ela não elimina a necessidade de estudo profundo, validações constantes e pensamento autoral. O uso responsável, com verificação de dados, respeito às políticas acadêmicas e transparência na produção, é o caminho para aproveitar o melhor desses recursos sem comprometer sua credibilidade.</p></div></div>"
}

# Simulando o request com o dicionário (sem usar o Werkzeug)
class MockRequest:
    def __init__(self, data):
        self.data = json.dumps(data).encode('utf-8')
        
    def get_json(self, silent=False):
        return json.loads(self.data.decode('utf-8'))

# Criando a instância do request simulado
mock_request = MockRequest(data)

# Agora, chamamos a função diretamente
response = function_handler(mock_request)

print(response)