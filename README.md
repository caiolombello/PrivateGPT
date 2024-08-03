# Private GPT

## Description
**Private GPT** is a customized version of OpenAI's ChatGPT, designed to provide a powerful and versatile interaction experience with artificial intelligence technologies. This assistant can transform how you utilize AI in various daily applications.

## Features
- **Interactive Chat**: View your OpenAI balance, create and manage different chats, and switch assistants during a conversation.
- **AI Audio Generation**: Create high-quality audio in seconds.
- **Artist Assistant**: Generate stunning images, like forest landscapes, with the artist AI.
- **Scriptwriter Assistant**: Create creative and efficient scripts, such as horror video scripts.

## Project Structure
- **routes/**: Contains application routes.
- **assistants/**: Module for managing assistants.
- **instance/**: Directory to store generated files, such as audio.
- **static/**: Static files (CSS, JS, images).
- **templates/**: HTML templates for rendering in Flask.
- **app.py**: Entry point of the Flask application.
- **config.py**: Application configuration.
- **models.py**: Database models definition.

## Installation and Configuration
1. Clone the repository:
    ```sh
    git clone https://github.com/caiolombello/PrivateGPT.git
    cd PrivateGPT
    ```

2. Create and activate a virtual environment (optional, but recommended):
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install project dependencies:
    ```sh
    poetry install
    ```

4. Create a `.env` file with the following variables:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    OPENAI_SESSION_KEY=your_openai_session_key
    OPENAI_ORGANIZATION=your_openai_organization_id
    AUTHENTICATION=False
    ```

    - **OPENAI_API_KEY**: Your OpenAI API key, which you can obtain from your OpenAI account dashboard.
    - **OPENAI_SESSION_KEY**: Your OpenAI session key. For a detailed guide on how to get your session key, refer to [this discussion](https://github.com/ChatGPTNextWeb/ChatGPT-Next-Web/discussions/2936).
    - **OPENAI_ORGANIZATION**: Your OpenAI organization ID, which can be found in the [OpenAI platform settings](https://platform.openai.com/settings/organization/general).
    - **AUTHENTICATION**: Set to `False` if you do not require IP-based authentication; otherwise, set to `True` and configure accordingly.

5. Initialize the database:
    ```sh
    flask db init
    flask db migrate
    flask db upgrade
    ```

6. Run the application:
    ```sh
    flask run
    ```

## Usage
- **Create an Assistant**: Send a POST request to `/assistant/create` with `assistant_name`, `assistant_instructions`, `image` (optional), and `voice` (optional).
- **Initialize a Thread**: Send a POST request to `/assistant/initialize` with `assistant_id`.
- **List Assistants**: Send a GET request to `/assistant/list`.
- **Send Message**: Send a POST request to `/messages/send` with `thread_name` and `message`.
- **Receive Messages**: Send a GET request to `/messages/receive/<thread_name>`.
- **Rename Thread**: Send a POST request to `/messages/thread/rename` with `thread_name` and `messages`.

## Docker
To build and run the application with Docker:

1. Build the Docker image:
    ```sh
    docker build -t private-gpt .
    ```

2. Run the container:
    ```sh
    docker run -d -p 5000:5000 --name private-gpt-container private-gpt
    ```

## Assistant Creation Script
The `create.sh` script located in the `assistants` folder can be used to automatically create assistants based on instruction files.

1. Edit the `create.sh` script to adjust the `SERVER_URL` if necessary.
2. Add or modify text files with the assistant instructions in the `assistants` folder.
3. Run the script:
    ```sh
    ./assistants/create.sh
    ```

## Contribution
Contributions are welcome! Feel free to open issues and pull requests to improve this project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For more information, contact [caio@lombello.com](mailto:caio@lombello.com).
