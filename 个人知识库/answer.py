import dashscope
from dashscope import Generation
from search import search_relevant_news


def answer_question(question, context):
    prompt = f"""请基于```内的内容回答问题。
    ```
    {context}
    ```
    我的问题是：{question}
    """
    print(prompt)

    rsp = Generation.call(model='qwen-turbo', prompt=prompt)
    return rsp.output.text


if __name__ == '__main__':
    dashscope.api_key = 'sk-103756eb54634450bc4f5ac7c012c8e5'
    question = '中铁十四局办公大楼所在地在哪？'
    context = search_relevant_news(question)
    print(answer_question(question, context))
