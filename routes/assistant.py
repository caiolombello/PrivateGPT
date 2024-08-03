from flask import jsonify, request
from . import assistant_bp
from models import db, Assistant, Thread
from openai import OpenAI
import os
from uuid import uuid4

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_or_create_assistant(name, instructions, image=False, voice=False):
    assistant_record = Assistant.query.filter_by(name=name).first()
    if assistant_record:
        return assistant_record.assistant_id

    assistants = client.beta.assistants.list(limit=100)
    existing_assistant = next((asst for asst in assistants.data if asst.name == name), None)

    if existing_assistant:
        assistant_id = existing_assistant.id
        new_assistant = Assistant(assistant_id=assistant_id, name=name)
        db.session.add(new_assistant)
        db.session.commit()
        return assistant_id

    # Define the tools based on the parameters
    tools = []
    if image:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_image",
                "description": "Generate an image based on a text prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "The text prompt to generate the image for"},
                        "size": {"type": "string", "description": "The size of the image", "default": "1792x1024"}
                    },
                    "required": ["prompt"]
                }
            }
        })

    if voice:
        tools.append({
            "type": "function",
            "function": {
                "name": "generate_speech",
                "description": "Generate speech based on a text input",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "The text to convert to speech"},
                        "voice": {"type": "string", "description": "The voice to use for the speech", "default": "alloy"}
                    },
                    "required": ["text"]
                }
            }
        })

    tool_enabled = False
    if voice or image:
        tool_enabled = True

    assistant = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model="gpt-4o",
        tools=tools
    )
    assistant_id = assistant.id
    new_assistant = Assistant(assistant_id=assistant_id, name=name, tool_enabled=tool_enabled)
    db.session.add(new_assistant)
    db.session.commit()
    return assistant_id

@assistant_bp.route('/create', methods=['POST'])
def create_assistant():
    try:
        data = request.json
        assistant_name = data.get('assistant_name')
        assistant_instructions = data.get('assistant_instructions')
        image = data.get('image', False)
        voice = data.get('voice', False)

        if not assistant_name or not assistant_instructions:
            return jsonify({"error": "Assistant name and instructions are required"}), 400

        assistant_id = get_or_create_assistant(assistant_name, assistant_instructions, image=image, voice=voice)

        return jsonify({"status": "Assistant created or already exists", "assistant_id": assistant_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@assistant_bp.route('/initialize', methods=['POST'])
def initialize_thread():
    try:
        data = request.json
        assistant_id = data.get('assistant_id')

        if not assistant_id:
            assistant_record = Assistant.query.first()
            if not assistant_record:
                # Fetch the list of assistants from OpenAI
                assistants = client.beta.assistants.list(
                    order="desc",
                    limit=20
                )
                if not assistants.data:
                    return jsonify({"error": "No assistants available"}), 400
                
                # Save assistants to the database
                for asst in assistants.data:
                    new_assistant = Assistant(
                        assistant_id=asst.id,
                        name=asst.name,
                        tool_enabled=False
                    )
                    db.session.add(new_assistant)
                
                db.session.commit()

                # Use the first assistant from the list
                assistant_id = assistants.data[0].id

            else:
                assistant_id = assistant_record.assistant_id

        thread = client.beta.threads.create()
        thread_name = thread.id

        new_thread = Thread(id=str(uuid4()), name=thread_name, assistant_id=assistant_id, chat_name="New chat")
        db.session.add(new_thread)
        db.session.commit()

        return jsonify({"status": "Assistant and thread initialized successfully", "assistant_id": assistant_id, "thread_name": thread_name, "chat_name": "New chat"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@assistant_bp.route('/list', methods=['GET'])
def list_assistants():
    try:
        assistants = client.beta.assistants.list(
            order="desc",
            limit=20
        )
        
        # Manually convert the assistant objects to dictionaries
        assistants_data = []
        for asst in assistants.data:
            assistants_data.append({
                "id": asst.id,
                "name": asst.name,
                "model": asst.model
            })

        return jsonify({"assistants": assistants_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
