# https://huggingface.co/spaces/MAGAer13/mPLUG-Owl/blob/main/app.py
# https://huggingface.co/spaces/MAGAer13/mPLUG-Owl2
# https://github.com/allenai/s2-folks/blob/main/examples/python/find_and_recommend_papers/find_papers.py
# https://www.gradio.app/guides/creating-a-chatbot-fast
# https://huggingface.co/spaces/librarian-bots/recommend_similar_papers/blob/main/app.py
# https://huggingface.co/spaces/badayvedat/LLaVA
"""
This file demos a simple chatbot based on gradio and openai api
"""
import pathlib, json
import time
import gradio as gr
import os
import re
import argparse
import requests
from openai import OpenAI
from typing import Any
import datetime
import pandas as pd
from evaluate import load
import ollama

# Set openai credentials
# openai.api_key = os.environ.get("OPENAI_API_KEY")
S2_API_KEY = os.getenv('S2_API_KEY')

client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)

# Function to set the OpenAI API key
def set_apikey(api_key):
    if 'OPENAI_API_KEY' not in os.environ:
        os.environ['OPENAI_API_KEY'] = api_key
    return "OpenAI API key is Set"


def get_conv_log_filename():
    t = datetime.datetime.now()
    cur_dir = pathlib.Path(__file__).parent.resolve()
    log_dir = f"{cur_dir}/logs/"
    os.makedirs(log_dir, exist_ok=True)
    name = os.path.join(log_dir, f"{t.year}-{t.month:02d}-{t.day:02d}-conv.json")
    return name


def vote_last_response(state, vote_type, request: gr.Request):
    with open(get_conv_log_filename(), "a") as fout:
        data = {
            "tstamp": round(time.time(), 4),
            "type": vote_type,
            "state": state, #.dict(),
            "ip": request.client.host,
        }
        fout.write(json.dumps(data) + "\n")


def upvote_last_response(state, request: gr.Request):
    # logger.info(f"upvote. ip: {request.client.host}")
    vote_last_response(state, "upvote", request)
    return ""


def downvote_last_response(state, request: gr.Request):
    # logger.info(f"downvote. ip: {request.client.host}")
    vote_last_response(state, "downvote", request)
    return ""



example_abstract = """We explore the zero-shot abilities of recent large language models (LLMs) for the task of writing the literature review of a scientific research paper conditioned on its abstract and the content of related papers."""

examples_html = [
    f"<div style='text-align: left;'>{example_abstract}</div>"
]
# Create a custom HTML block to left-align text
custom_html = "<div style='text-align: left;'>Examples:</div>"


title_markdown = ("""
<h1 align="center"><a href=""><img src="/file=resources/download.png", alt="Writing Assistant - LitCraft" border="0" style="margin: 0 auto; height: 50px;" /></a> </h1>
<h2 align="center">🔥 LitLLM: A Toolkit for Scientific Literature Review</h2>
""")
# <h5 align="center"> If you like our project, please give us a star ✨ on Github for latest update.  </h2>

tos_markdown = ("""
### Terms of use
By using this service, users are required to agree to the following terms:
The service is a research preview intended for non-commercial use only. It only provides limited safety measures and may generate offensive content. It must not be used for any illegal, harmful, violent, racist, or sexual purposes. The service may collect user data for future research.
For an optimal experience, please use desktop computers for this demo, as mobile devices may compromise its quality.
""")


learn_more_markdown = ("""
### License
The service is a research preview intended for non-commercial use only, subject to the [Terms of Use](https://openai.com/policies/terms-of-use) of the data generated by OpenAI, and [Privacy Practices](https://chrome.google.com/webstore/detail/sharegpt-share-your-chatg/daiacboceoaocpibfodeljbdfacokfjb) of ShareGPT. Please contact us if you find any potential violation.
""")



block_css = """

h1 {
    text-align: center;
    display:block;
}

h2 {
    text-align: center;
    display:block;
}

#buttons button {
    min-width: min(120px,100%);
}

#display_mrkdwn {
    display: block;
    border-width: var(--block-border-width);
    border-color: var(--block-border-color);
    border-radius: var(--block-radius);
    background: var(--block-background-fill);
    padding: var(--input-padding);   
}

.gallery.svelte-1viwdyg {
    text-align: justify;
}

"""

def parse_arxiv_id_from_paper_url(url):
    arxiv_id = url.split("/")[-1]
    if arxiv_id[-4:] == ".pdf":
        arxiv_id = arxiv_id[:-4]
    return arxiv_id


def load_json(path: str) -> Any:
    """
    This function opens and JSON file path
    and loads in the JSON file.

    :param path: Path to JSON file
    :type path: str
    :return: the loaded JSON file
    :rtype: dict
    """
    with open(path, "r",  encoding="utf-8") as file:
        json_object = json.load(file)
    return json_object


def load_all_prompts(file_path: str = None) -> str:
    """
    Loads the api key from json file path

    :param file_path:
    :return:
    """
    cur_dir = pathlib.Path(__file__).parent.resolve()
    # Load prompts from file
    if not file_path:
        # Default file path
        file_path = f"{cur_dir}/resources/prompts.json"
    prompts = load_json(file_path)

    return prompts


def run_open_ai_api(json_data, model_name="llama3.1", max_tokens: int = 500, temperature: float = 0.2) -> str:
    """
    This function actually calls the OpenAI API
    Models such as gpt-4-32k, gpt-4-1106-preview
    :param json_data:
    :return:
    """
    print("this ran")
    completion = client.chat.completions.create(
        model=model_name,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{json_data['prompt']}"},
        ],
    )

    print(completion.choices[0])

    
    # response = ollama.chat(model=model_name, messages=[
    #     {"role": "system", "content": "You are a helpful assistant."},
    #             {"role": "user", "content": f"{json_data['prompt']}"},
    # ])
    # print(response['message']['content'])
        # stream=True
    # partial_message = ""
    # for chunk in completion:
    #     if len(chunk['choices'][0]['delta']) != 0:
    #         partial_message = partial_message + chunk['choices'][0]['delta']['content']
    #         yield partial_message
    return completion.choices[0].message.content

    # return response['message']['content']



def format_results_into_markdown(recommendations):
    comment = "The following papers were found by the Semantic Scholar API \n\n"
    for index, r in enumerate(recommendations):
        # hub_paper_url = f"https://huggingface.co/papers/{r['externalIds']['ArXiv']}"
        # comment += f"* [{r['title']}]({hub_paper_url}) ({r['year']})\n"
        comment += f"[{index+1}] [{r['title']}]({r['url']}) ({r['year']}) Cited by {r['citationCount']} <br>"
    return comment

def find_basis_paper(query, num_papers_api=20):
    fields = 'title,url,abstract,citationCount,journal,isOpenAccess,fieldsOfStudy,year,journal'
    rsp = requests.get('https://api.semanticscholar.org/graph/v1/paper/search',
                        headers={'X-API-KEY': S2_API_KEY},
                           params={'query': query, 'limit': num_papers_api, 'fields': fields})
    rsp.raise_for_status()
    results = rsp.json()
    total = results["total"]
    if not total:
        print('No matches found. Please try another query.')

    print(f'Found {total} results. Showing up to {num_papers_api}.')
    papers = results['data']
    # df = pd.DataFrame(papers)
    return papers #[:result_limit]

def get_recommendations_from_semantic_scholar(url: str, num_papers_api=20):
    """
    https://www.semanticscholar.org/product/api/tutorial
    """
    fields = 'title,url,abstract,citationCount,journal,isOpenAccess,fieldsOfStudy,year,journal'
    arxiv_id = parse_arxiv_id_from_paper_url(url)
    query_id = f"ArXiv:{arxiv_id}"

    rsp = requests.post(
            "https://api.semanticscholar.org/recommendations/v1/papers/",
            json={
                "positivePaperIds": [query_id],
            },
            params={"fields": fields, "limit": num_papers_api},
        )

    results = rsp.json()
    papers = results['recommendedPapers']
    return papers

def get_paper_data(paper_url):
    """
    Retrieves data of one paper based on URL
    """
    fields = 'title,url,abstract,citationCount,journal,isOpenAccess,fieldsOfStudy,year,journal'
    rsp = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/URL:{paper_url}",
                       headers={'X-API-KEY': S2_API_KEY},
                       params={'fields': fields})
    results = rsp.json()
    return results


def sort_papers(papers, sort_by):
    """
    sort by categories: "Relevance", "Citations", "Year
    """
    df = pd.DataFrame(papers)        
    if sort_by == "Citations":
        df = df.sort_values(by="citationCount", ascending=False)
    elif sort_by == "Year":
        df = df.sort_values(by="year", ascending=False)    
    papers_list = df.to_dict(orient='records')
    return papers_list


def get_markdown_query_text(papers):
    display_markdown = format_results_into_markdown(papers)
    cite_text = format_abstracts_as_references(papers)
    return display_markdown, cite_text


def filter_recommendations(recommendations, max_paper_count=5):
    # include only arxiv papers
    arxiv_paper = [
        r for r in recommendations if r["externalIds"].get("ArXiv", None) is not None
    ]
    if len(arxiv_paper) > max_paper_count:
        arxiv_paper = arxiv_paper[:max_paper_count]
    return arxiv_paper

# def format_recommendation_into_markdown(arxiv_id, recommendations):
#     comment = "The following papers were recommended by the Semantic Scholar API \n\n"
#     for r in recommendations:
#         hub_paper_url = f"https://huggingface.co/papers/{r['externalIds']['ArXiv']}"
#         comment += f"* [{r['title']}]({hub_paper_url}) ({r['year']})\n"
#     return comment


def format_abstracts_as_references(papers):
    # cite_list = ["@cite_1", "@cite_2", "@cite_3"]
    cite_text = ""
    for index, paper in enumerate(papers):
        # citation = f"@cite_{index+1}"
        citation = f"{index+1}"
        cite_text = f"{cite_text}[{citation}]: {paper['abstract']}\n"
    return cite_text

def format_prompt(base_prompt, abstract, cite_text, plan=""):
    if plan:
        data = f"Abstract: {abstract} \n {cite_text} \n Plan: {plan}"
    else:
        data = f"Abstract: {abstract} \n {cite_text}"
    complete_prompt = f"{base_prompt}\n```{data}```"
    return complete_prompt

def get_complete_prompt_for_summarization(base_prompt, data):
    """
    This prompt helps in getting keywords to be used by S2 API
    """
    complete_prompt = f"{base_prompt}\n```Abstract: {data}```"
    return complete_prompt

def check_matching_paper(wer, abstract, papers, check_papers: int =3, wer_threshold = 0.12):
    """
    Check if the user put the abstract of already existing paper and it is in the retrieved papers. 
    Using Word error rate as the metric on the top check_papers
    """
    references = [abstract]
    for i in range(check_papers):
        predictions = [papers[i]['abstract']]
        wer_score = wer.compute(predictions=predictions, references=references)
        if wer_score < wer_threshold:
            papers.pop(i)
            return papers
    return papers


class GradioChatApp:
    """
    Class to define Gradio based chat app
    """

    def __init__(self):
        self.name = "GradioChatApp"
        self.prompts = load_all_prompts()
        self.role_template = self.prompts["role_template"] 
        self.plan_prompt = self.prompts["plan_template"] 
        self.vanilla_prompt = self.prompts["vanilla_template"] 
        self.sample_plan = self.prompts["plan"]
        self.summarization_prompt = self.prompts["summarization_template"]
        self.ranking_prompt = self.prompts["ranking_template"]
        self.wer = load("wer")

    def add_text(self, history, text, base_paper_textbox, keyword_textbox, rerank: bool = True, 
                 num_papers: int = 3, model_name="llama3.1", sort_by="relevance", temperature = 0.2, max_tokens = 300, num_papers_api: int = 20):
        """
        Add text to history
        """
        # if 'OPENAI_API_KEY' not in os.environ:
        #     raise gr.Error('Upload your OpenAI API key')

        history = history + [(f"User provided abstract: \n {text}", None)]
        # print("All textboxes:", plan_textbox, base_paper_textbox, keyword_textbox)
        try: 
            if base_paper_textbox:
                hist_response = f"Finding recommendations from S2 API based on the paper \n {base_paper_textbox}"
                papers = get_recommendations_from_semantic_scholar(base_paper_textbox, num_papers_api)
            else:
                if keyword_textbox:
                    query = keyword_textbox
                else:
                    # query = "multi document summarization"
                    prompt = get_complete_prompt_for_summarization(self.summarization_prompt, text)
                    json_data = {"prompt": prompt}
                    print(json_data)
                    query = run_open_ai_api(json_data, model_name=model_name, max_tokens=max_tokens, temperature=temperature)
                print(query)
                hist_response = f"LLM summarized keyword query to be used for S2 API: \n {query}"
                papers = find_basis_paper(query, num_papers_api)
        except:
            history = history + [("No papers found using S2. Try providing keywords or a seed paper!", None)]
            return history, "", "No papers found", "", "", ""
        if not papers:
            history = history + [("No papers found using S2. Try providing keywords or changing seed paper!", None)]
            return history, "", "No papers found", "", "", ""
        history = history + [(hist_response, None)]
        # print(rerank, sort_by)
        try:
            papers = check_matching_paper(self.wer, text, papers)
        except:
            print("WER failed")
        papers = sort_papers(papers, sort_by)
        display_markdown, cite_text = get_markdown_query_text(papers)
        if rerank == "True":
            # print(f"{self.role_template}{self.ranking_prompt}")
            try:
                complete_prompt = format_prompt(base_prompt=f"{self.role_template} {self.ranking_prompt}", abstract=text, cite_text=cite_text)
                json_data = {"prompt": complete_prompt}
                response = run_open_ai_api(json_data, model_name=model_name, max_tokens=max_tokens, temperature=temperature)
                # print(response)
                # [1] > [2] > [4] > [3] > [6] > [5]
                new_order = [int(s) for s in re.findall(r'\d+', response)]    
                # print(new_order)        
                papers = [papers[i-1] for i in new_order]
            except:
                print("LLM not able to rerank!")

        # If paper based on seed paper, insert it at 0th index
        if base_paper_textbox:
            try:
                base_paper_data = get_paper_data(paper_url=base_paper_textbox)
                papers.insert(0,base_paper_data)
            except:
                print("Cant retrieve data for base paper!")
        papers = papers[:num_papers]
        display_markdown, cite_text = get_markdown_query_text(papers)
        
        return history, text, display_markdown, cite_text, base_paper_textbox, keyword_textbox

    def bot(self, history, cite_text, text, plan_textbox, request: gr.Request, model_name="gpt-4", 
            temperature = 0.2, max_tokens = 300, regenerate: bool = False):
        """
        Calls the openai api
        """
        # if 'OPENAI_API_KEY' not in os.environ:
        #     raise gr.Error('Upload your OpenAI API key')

        # Cache headers, ip address
        # if request:
            # print("Request headers dictionary:", request.headers)
            # print("IP address:", request.client.host)
        if cite_text =="":
            return "How may I help?"
        if plan_textbox:
            complete_prompt = format_prompt(base_prompt=self.plan_prompt, abstract=text, cite_text=cite_text, plan=plan_textbox)
            # history = history + [(f"Using plan: \n {plan_textbox}", None)]
        else:
            self.vanilla_prompt = self.vanilla_prompt.format(max_tokens=max_tokens)
            # print(self.vanilla_prompt)
            complete_prompt = format_prompt(base_prompt=self.vanilla_prompt, abstract=text, cite_text=cite_text, plan="")
        # print(complete_prompt)

        # if regenerate=="True":
        #     history.pop()
        # print(complete_prompt)
        json_data = {"prompt": complete_prompt}
        print("I was here")
        response = run_open_ai_api(json_data, model_name=model_name, max_tokens=max_tokens, temperature=temperature)

        history[-1][1] = ""
        for character in response:
            history[-1][1] += str(character)
            time.sleep(0.005)
            yield history
        # history[-1][1] = response
        # time.sleep(1)
        # yield history

    def launch_app(self):
        """
        Gradio app defined here
        """
        # Close all apps running on servers
        gr.close_all()
        textbox = gr.Textbox(lines=2, show_label=False, placeholder="Enter the abstract of your paper", container=False)
        plan_textbox = gr.Textbox(show_label=False, placeholder="Enter sentence plan (Default none). Example: Cite [1] on line 2.", container=False)
        base_paper_textbox = gr.Textbox(show_label=False, placeholder="Provide link of most relevant paper", container=False)
        keyword_textbox = gr.Textbox(show_label=False, placeholder="Enter optional keywords for querying (Default none)", container=False)

        with gr.Blocks(title="Writing Assistant", theme=gr.themes.Default(), css=block_css) as demo:
            prompt = gr.State()

            gr.Markdown(title_markdown)
            # with gr.Row():
            #     gr.Image("resources/download.png", width=64, height=64)
            with gr.Accordion("How to use (click to expand)", open=False):
                gr.Markdown(
                    """ 
                    Search and write literature review for your research idea/proposal or a draft abstract with this powerful AI tool. 
                    TLDR; We query Semantic Scholar (S2) to retrieve relevant papers and optionally rerank them using another LLM. 
                    With the principles of Retrieval Augmented Generation, LLM generates the related work section for your paper. 
                    
                    There are three strategies for AI search:
                    * We summarize your abstract with GPT-4 to get keywords which are then used to search S2
                    * You provide keywords that could be used as a search query
                    * Provide a seed paper used for recommendation

                    For generation, you could also provide a sentence plan to the LLM which contains the number of sentences and citations to produce
                    """
                )

            with gr.Row():
                with gr.Column(scale=3):

                    # TODO: OpenAI Keys
                    # with gr.Accordion("OpenAI key", open=False) as key_row:
                    #     with gr.Row():
                    #         api_key = gr.Textbox(placeholder='Enter OpenAI API key', show_label=False, interactive=True, scale=3)
                    #         change_api_key = gr.Button('Change Key', scale=1)

                    with gr.Accordion("Ranking Parameters", open=False) as parameter_row:
                        # https://platform.openai.com/docs/models/overview
                        model_name = gr.Dropdown(["llama3.1"], value="llama3.1", interactive=True,  label="Model") # scale=1, min_width=0
                        num_papers = gr.Slider(minimum=1, maximum=10, value=4, step=1, interactive=True, label="Cite # papers")
                        sort_by = gr.Dropdown(["Relevance", "Citations", "Year"], value="Relevance", interactive=True,  label="Sort by") # scale=1, min_width=0
                        llm_rerank = gr.Radio(choices=["True", "False"], value="True", interactive=True, label="LLM Re-rank (May override sorting)")
                        with gr.Row():
                            temperature = gr.Slider(minimum=0.0, maximum=1.0, value=0.2, step=0.1, interactive=True, label="Temperature", scale=1)
                            max_tokens = gr.Slider(minimum=0, maximum=3000, value=500, step=64, interactive=True, label="Max output tokens", scale=2)
                    display_1 = gr.Markdown(value=f"Retrieved papers", label="Retrieved papers!", elem_id="display_mrkdwn") #, visible=True)
                    # with gr.Accordion("Generation Parameters", open=False) as parameter_row:
                        # top_p = gr.Slider(minimum=0.0, maximum=1.0, value=0.7, step=0.1, interactive=True, label="Top P")

                with gr.Column(scale=8):
                    chatbot = gr.Chatbot(elem_id="Chatbot", label="ReviewGPT", height=480)

            with gr.Row():
                with gr.Column(scale=3):

                    with gr.Accordion("Example", open=False) as example_row:
                        gr.Examples(label="Example: Abstract", examples=[
                            [example_abstract], 
                        ], inputs=[textbox], elem_id="example_abstract")
                        gr.Examples(label="Example: Query keywords (Optional)", examples=[
                            ["multi document summarization of scientific articles"],
                        ], inputs=[keyword_textbox])
                        gr.Examples(label="Example: Most relevant paper (Optional)", examples=[
                            ["https://arxiv.org/abs/2010.14235"],
                        ], inputs=[base_paper_textbox])
                        gr.Examples(label="Example: Sentence plan (Optional)", examples=[
                            [self.sample_plan],
                        ], inputs=[plan_textbox])

                with gr.Column(scale=8):

                    with gr.Row():
                        with gr.Column(scale=6):
                            textbox.render()
                        with gr.Column(scale=1, min_width=50):
                            submit_btn = gr.Button(value="Send", variant="primary")
                    with gr.Row():
                        gr.Markdown("""Optionally, improve the API Search by either providing keywords or a very relevant seed paper. Seed paper takes priority if provided both.""")
                    with gr.Row():
                        with gr.Column(scale=2):
                            keyword_textbox.render()
                        with gr.Column(scale=2):
                            base_paper_textbox.render()
                    with gr.Row():
                        gr.Markdown("""Optionally, provide a sentence plan to be used for generation""")
                    with gr.Row():
                        with gr.Column(scale=5):
                            plan_textbox.render()
                        with gr.Column(scale=2, min_width=50):
                            plan_generate_btn = gr.Button(value="Regenerate with plan", variant="primary")
                    # with gr.Row(elem_id="buttons") as button_row:
                    #     upvote_btn = gr.Button(value="👍  Upvote")
                    #     downvote_btn = gr.Button(value="👎  Downvote")
                    #     # flag_btn = gr.Button(value="⚠️  Flag", interactive=False)
                    #     # #stop_btn = gr.Button(value="⏹️  Stop Generation", interactive=False)
                    #     regenerate_btn = gr.Button(value="🔄  Regenerate")
                    #     clear_btn = gr.Button(value="🗑️  Clear")

            gr.Markdown(tos_markdown)
            gr.Markdown(learn_more_markdown)


            # btn_list = [regenerate_btn, clear_btn]

            # TODO: OpenAI Keys
            # api_key.submit(fn=set_apikey, inputs=[api_key], outputs=[api_key])
            # change_api_key.click(fn=set_apikey, inputs=[api_key], outputs=[api_key])


            textbox.submit(
                self.add_text,
                [chatbot, textbox, base_paper_textbox, keyword_textbox, llm_rerank, num_papers, model_name, sort_by, temperature, max_tokens],
                [chatbot, textbox, display_1, prompt, base_paper_textbox, keyword_textbox],
                queue=False
            ).then(
                self.bot,
                [chatbot, prompt, textbox, plan_textbox, model_name, temperature, max_tokens],
                [chatbot]
            )
            submit_btn.click(
                self.add_text,
                [chatbot, textbox, base_paper_textbox, keyword_textbox, llm_rerank, num_papers, model_name, sort_by, temperature, max_tokens],
                [chatbot, textbox, display_1, prompt, base_paper_textbox, keyword_textbox],
                queue=False
            ).then(
                self.bot,
                [chatbot, prompt, textbox, plan_textbox, model_name, temperature, max_tokens],
                [chatbot]
            )

            plan_generate_btn.click(self.bot,
                [chatbot, prompt, textbox, plan_textbox, model_name, temperature, max_tokens],
                [chatbot])
            # upvote_btn.click(upvote_last_response, prompt, [textbox], queue=False)
            # downvote_btn.click(downvote_last_response, prompt, [textbox], queue=False)


            # regenerate_btn.click(self.bot,
            #     [chatbot, prompt, textbox, plan_textbox, model_name, temperature, max_tokens],
            #     [chatbot])
            # # state can also be cached  https://github.com/gradio-app/gradio/issues/730
            # txt.submit(self.add_text, [chatbot, txt], [chatbot, txt]).then(
            #     self.bot, chatbot, chatbot
            # )
            # clear_btn.click(lambda: None, None, chatbot, queue=False)

        demo.launch(allowed_paths=["resources/"])


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--debug", action="store_true", help="using debug mode")
    parser.add_argument("--port", type=int)
    parser.add_argument("--concurrency-count", type=int, default=1)


    # demo = build_demo()
    # demo.queue(concurrency_count=args.concurrency_count, 
    #            status_update_rate=10, api_open=False).launch(server_name=args.host, 
    #            debug=args.debug, server_port=args.port, share=False)


    test_app = GradioChatApp()
    test_app.launch_app()
