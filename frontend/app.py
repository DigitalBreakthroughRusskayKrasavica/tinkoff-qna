import gradio as gr
import requests

API_URL = 'http://localhost:8000'

def send_to_api(question: str) -> str:
    res = requests.post(
        url=API_URL + '/assist', 
        json={'title': question},
        headers={"Content-Type": "application/json; charset=utf-8"},
    ).json()

    answer, links = res['title'], '\n'.join(res['links'])
    return f'{answer}\n\nПодробнее:\n{links}'


with gr.Blocks() as demo:
    question = gr.Text(
        label='Ваш вопрос',
    )
    answer = gr.Text(
        label='Ответ на вопрос',
    )
    send_question_btn = gr.Button(
        'Отправить вопрос'
    )
    send_question_btn.click(
        fn=send_to_api,
        inputs=question,
        outputs=answer
    )


if __name__ == '__main__':
    demo.launch(share=True, server_port=8042)
