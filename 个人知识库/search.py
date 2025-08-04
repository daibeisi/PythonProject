from dashvector import Client

from embedding import generate_embeddings


def search_relevant_news(question):
    # 初始化 dashvector client
    client = Client(
        api_key='sk-S1VBtC7EtBWzTalWqrNtAE8QPkIec79E0D455605C11EFAC1BFE62EA484838',
        endpoint='vrs-cn-cfn3vspqm0002u.dashvector.cn-shanghai.aliyuncs.com'
    )

    # 获取刚刚存入的集合
    collection = client.get('news_embedings')
    assert collection

    # 向量检索：指定 topk = 1
    rsp = collection.query(generate_embeddings(question), output_fields=['raw'], topk=1)
    assert rsp
    return rsp.output[0].fields['raw']