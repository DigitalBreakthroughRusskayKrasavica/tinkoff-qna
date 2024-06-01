
import requests

API_URL = 'http://147.45.252.109:8000'

import gradio as gr
import speech_recognition as sr


def send_to_api(question: str) -> str:
    res = requests.post(
        url=API_URL + '/assist',
        json={'title': question},
        headers={"Content-Type": "application/json; charset=utf-8"},
    ).json()

    answer, links = res['title'], '\n'.join(res['links'])
    return f'{answer}\n\nПодробнее:\n{links}'


r = sr.Recognizer()


def transcribe_audio(path):
    # use the audio file as the audio source
    with sr.AudioFile(path) as source:
        audio_listened = r.record(source)
        # try converting it to text
        text = r.recognize_google(audio_listened, language="ru-RU")
    return text


def get_answer(question: str, audio: str) -> tuple[str, str, None]:
    if not (audio or question):
        return 'send audio or question', '', None
    if not question:
        return send_to_api(transcribe_audio(audio)), '', None
    return send_to_api(question), '', None


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(variant='panel'):
            gr.Markdown('# Введите ваш вопрос текстом или голосом:')
            question = gr.Text(show_label=False)
            audio = gr.Audio(show_label=False, type='filepath')
            send_question_btn = gr.Button('Отправить вопрос')

        with gr.Column(variant='panel'):
            gr.Markdown('# Ответ на ваш вопрос:')
            answer = gr.Markdown(line_breaks=True)

    send_question_btn.click(
        fn=get_answer,
        inputs=[question, audio],
        outputs=[answer, question, audio]
    )

if __name__ == '__main__':
    demo.launch(share=True, server_port=8042)
