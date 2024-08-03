from flask import jsonify, request, Response, stream_with_context, send_from_directory
from . import messages_bp
from models import db, Message, Thread
from openai import OpenAI, AssistantEventHandler
from openai.types.beta.threads import Text, TextDelta
import os
import json
from uuid import uuid4
from pathlib import Path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class EventHandler(AssistantEventHandler):   
    def __init__(self):
        super().__init__()
        self.response = ""

    def on_text_delta(self, delta: TextDelta, snapshot: Text) -> None:
        self.response += delta.value

    def on_event(self, event):
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            arguments = json.loads(tool.function.arguments)
            if tool.function.name == "generate_image":
                prompt = arguments.get('prompt')
                size = arguments.get('size', '1792x1024')
                image_url = self.generate_image(prompt, size)
                tool_outputs.append({"tool_call_id": tool.id, "output": image_url})
            elif tool.function.name == "generate_speech":
                text = arguments.get('text')
                voice = arguments.get('voice', 'alloy')
                speech_url = self.generate_speech(text, voice)
                tool_outputs.append({"tool_call_id": tool.id, "output": speech_url})

        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:
                self.response += text
            self.response = self.replace_sandbox_link(self.response)

    def replace_sandbox_link(self, response):
        import re
        match = re.search(r'sandbox:/mnt/data/(.*\.mp3)', response)
        if match:
            sandbox_path = match.group(0)
            filename = match.group(1)
            speech_url = f"http://pgpt.lombello.com:5000/messages/audio/{filename}"
            response = response.replace(sandbox_path, speech_url)
        return response

    def generate_image(self, prompt, size):
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"Failed to generate image: {e}")
            return ""

    def generate_speech(self, text, voice):
        try:
            speech_file_name = f"{uuid4()}.mp3"
            speech_file_path = Path(f"instance/{speech_file_name}")
            response = client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text
            )
            response.stream_to_file(speech_file_path)
            speech_url = f"http://pgpt.lombello.com:5000/messages/audio/{speech_file_name}"
            return speech_url
        except Exception as e:
            print(f"Failed to generate speech: {e}")
            return ""

@messages_bp.route('/receive/<thread_name>', methods=['GET'])
def receive_message(thread_name):
    thread = Thread.query.filter_by(name=thread_name).first()
    if not thread:
        return jsonify({"error": "Thread not found"}), 404
    assistant_id = thread.assistant_id

    def generate_response():
        handler = EventHandler()
        content = ""

        try:
            with client.beta.threads.runs.stream(
                thread_id=thread_name,
                assistant_id=assistant_id,
                event_handler=handler,
            ) as stream:
                for event in stream:
                    if handler.response:
                        content += handler.response
                        yield handler.response
                        handler.response = ""

            new_message = Message(thread_id=thread_name, role="assistant", content=content)
            db.session.add(new_message)
            db.session.commit()

        except Exception as e:
            yield f"[ERROR] {str(e)}"

    return Response(stream_with_context(generate_response()), content_type='text/plain')

@messages_bp.route('/send', methods=['POST'])
def send_message():
    data = request.json
    thread_name = data.get('thread_name')
    user_message = data.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = client.beta.threads.messages.create(
            thread_id=thread_name,
            role="user",
            content=user_message
        )

        new_message = Message(thread_id=thread_name, role="user", content=user_message)
        db.session.add(new_message)
        db.session.commit()

        return jsonify({"status": "Message sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@messages_bp.route('/threads', methods=['GET'])
def get_threads():
    threads = Thread.query.all()
    return jsonify([{"id": thread.id, "name": thread.name, "chat_name": thread.chat_name} for thread in threads])

@messages_bp.route('/thread/<thread_name>', methods=['DELETE'])
def delete_thread(thread_name):
    thread = Thread.query.filter_by(name=thread_name).first()
    if not thread:
        return jsonify({"error": "Thread not found"}), 404

    try:
        # Delete the thread in OpenAI
        client.beta.threads.delete(thread_id=thread_name)

        # Delete the thread and its messages in the local database
        messages = Message.query.filter_by(thread_id=thread_name).all()
        for message in messages:
            # Check if the message content contains a link to an audio file
            if "http://pgpt.lombello.com:5000/messages/audio/" in message.content:
                audio_file_name = message.content.split("http://pgpt.lombello.com:5000/messages/audio/")[-1]
                audio_file_path = Path(f"instance/{audio_file_name}")
                if audio_file_path.exists():
                    os.remove(audio_file_path)
            db.session.delete(message)
        
        db.session.delete(thread)
        db.session.commit()

        return jsonify({"status": "Chat deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@messages_bp.route('thread/<thread_name>', methods=['GET'])
def get_messages(thread_name):
    messages = Message.query.filter_by(thread_id=thread_name).all()
    return jsonify([{"id": message.id, "role": message.role, "content": message.content} for message in messages])

@messages_bp.route('/thread/rename', methods=['POST'])
def rename_thread():
    data = request.json
    thread_name = data.get('thread_name')
    messages = data.get('messages')
    if not messages:
        return jsonify({"error": "Messages are required"}), 400

    rename_messages = [
        { "role": "system", "content": "Baseado nas respostas de um assistente, em uma conversa, nomeie essa conversa. Você deverá trazer a resposta somente com o nome da conversa, nada mais." },
        { "role": "user", "content": "\n".join(m["content"] for m in messages) }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=rename_messages,
            max_tokens=10
        )
        new_name = response.choices[0].message.content.strip()
        
        # Atualizar o campo chat_name no banco de dados
        thread = Thread.query.filter_by(name=thread_name).first()
        if thread and new_name:
            thread.chat_name = new_name
            db.session.commit()

        return jsonify({"new_name": new_name}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

# Rota para servir arquivos de áudio
@messages_bp.route('/audio/<filename>', methods=['GET'])
def get_audio(filename):
    return send_from_directory('instance', filename)

# Rota para servir arquivos de imagem
@messages_bp.route('/image/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory('instance', filename)
