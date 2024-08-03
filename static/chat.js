document.addEventListener('DOMContentLoaded', () => {
    let API_URL_INITIALIZE, API_URL_SEND, API_URL_RECEIVE, API_URL_GET_THREADS, API_URL_GET_MESSAGES, API_URL_DELETE_THREAD, API_URL_RENAME_THREAD, API_URL_LIST_ASSISTANTS;
    let messageCount = 0; // Contador de mensagens
    let initialMessages = [];
    
    const fetchPublicIP = async () => {
        try {
            const response = await fetch('https://api64.ipify.org?format=json');
            const data = await response.json();
            
            // Extract IP from the response
            const userIP = data.ip;
    
            if (userIP) {
                console.log('Visitor: ' + userIP);
                // Send user's IP to the server for authentication
                const authResponse = await fetch('/authenticate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ ip: userIP }),
                });
    
                const authData = await authResponse.json();
                if (authData.authorized) {
                    initializeApplication();
                } else {
                    document.body.innerHTML = '<h1>Access Denied</h1>';
                }
            } else {
                document.body.innerHTML = '<h1>Access Denied</h1>';
                console.error('Unable to fetch user IP');
            }
        } catch (error) {
            document.body.innerHTML = '<h1>Access Denied</h1>';
            console.error('Error fetching public IP:', error);
        }
    }

    const showNotification = (message, isError = false) => {
        const notificationContainer = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = 'notification';
        if (isError) {
            notification.classList.add('error');
        }
        notification.innerText = message;
        notificationContainer.appendChild(notification);

        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notificationContainer.removeChild(notification);
            }, 300); // Correspondente ao tempo de transição em CSS
        }, 3000); // Duração da notificação
    };

    const initializeApplication = () => {
        const ip = "pgpt.lombello.com";
        API_URL_INITIALIZE = `http://${ip}:5000/assistant/initialize`;
        API_URL_SEND = `http://${ip}:5000/messages/send`;
        API_URL_RECEIVE = `http://${ip}:5000/messages/receive`;
        API_URL_GET_THREADS = `http://${ip}:5000/messages/threads`;
        API_URL_GET_MESSAGES = `http://${ip}:5000/messages`;
        API_URL_DELETE_THREAD = `http://${ip}:5000/messages/thread`;
        API_URL_RENAME_THREAD = `http://${ip}:5000/messages/thread/rename`;
        API_URL_LIST_ASSISTANTS = `http://${ip}:5000/assistant/list`;

        const promptInput = document.getElementById("promptInput");
        const generateBtn = document.getElementById("generateBtn");
        const stopBtn = document.getElementById("stopBtn");
        const resultText = document.getElementById("resultText");
        const threadSelect = document.getElementById("threadSelect");
        const assistantSelect = document.getElementById("assistantSelect");
        const newChatBtn = document.getElementById("newChatBtn");
        const deleteChatBtn = document.getElementById("deleteChatBtn");

        let currentThreadName = null;
        let currentChatName = "New chat";
        let assistantId = null;

        const initialize = async () => {
            const response = await fetch(API_URL_INITIALIZE, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ assistant_id: assistantSelect.value })
            });
            const data = await response.json();
            if (data.status === "Assistant and thread initialized successfully") {
                messageCount = 0;
                currentThreadName = data.thread_name;
                assistantId = data.assistant_id;
                addThreadOption({ thread_id: data.thread_name, chat_name: "New chat" });
                loadMessages(data.thread_name);
                showNotification("New chat created successfully", false);
            } else {
                console.error("Initialization failed:", data);
            }
        };

        const deleteThread = async () => {
            if (!currentThreadName) {
                showNotification("Please select a thread to delete.", true);
                return;
            }

            const response = await fetch(`${API_URL_DELETE_THREAD}/${currentThreadName}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            const data = await response.json();
            if (data.status === "Chat deleted successfully") {
                showNotification('Chat deleted successfully', false);
                removeThreadOption(currentThreadName);
                resultText.innerHTML = "";
                if (threadSelect.options.length > 0) {
                    currentThreadName = threadSelect.value;
                    loadMessages(currentThreadName);
                    messageCount = 0;
                } else {
                    currentThreadName = null;
                }
            } else {
                showNotification(`Failed to delete thread: ${data.error}`, true);
            }
        };

        const threadExists = (threadId) => {
            return Array.from(threadSelect.options).some(option => option.value === threadId);
        };

        const addThreadOption = (thread) => {
            if (!threadExists(thread.thread_id)) {
                const option = document.createElement("option");
                option.value = thread.thread_id;
                option.text = thread.chat_name;
                threadSelect.appendChild(option);
                threadSelect.value = thread.thread_id;
            }
        };

        const renameThreadOption = (threadName, newThreadName) => {
            const options = Array.from(threadSelect.options);
            const option = options.find(option => option.value === threadName);
            if (option) {
                option.text = newThreadName;
            }
        };

        const removeThreadOption = (threadName) => {
            const option = Array.from(threadSelect.options).find(option => option.value === threadName);
            if (option) {
                threadSelect.removeChild(option);
            }
        };

        const scrollToBottom = () => {
            const resultContainer = document.getElementById('resultContainer');
            resultContainer.scrollTop = resultContainer.scrollHeight;
        };

        const loadMessages = async (threadId) => {
            const response = await fetch(`${API_URL_GET_MESSAGES}/thread/${threadId}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });
            const data = await response.json();
            resultText.innerHTML = "";
            data.forEach((message) => {
                const regex = /\[.*?\]\((http:\/\/pgpt\.lombello\.com:5000\/messages\/audio\/[a-f0-9-]+\.mp3)\)/g;
                content = message.content.replaceAll(regex, '<audio controls src="$1"></audio>');
                addMessageToChat(content, message.role);
            });            
            scrollToBottom();
        };

        if (threadSelect) {
            threadSelect.addEventListener("change", (event) => {
                currentThreadName = event.target.value;
                currentChatName = event.target.text;
                loadMessages(currentThreadName);
            });
        }

        const addMessageToChat = (message, role) => {
            let messageElement;

            messageElement = document.createElement("div");
            messageElement.className = `message ${role === 'assistant' ? 'assistant-message' : 'user-message'}`;
            messageElement.innerHTML = marked.parse(message);
            resultText.appendChild(messageElement);
            scrollToBottom();
        };

        const renameThread = async (messages) => {
            console.log("Renomeando " + currentChatName);
            if (currentChatName === "New chat") {
                try {
                    const response = await fetch(API_URL_RENAME_THREAD, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            thread_name: currentThreadName,
                            messages: messages
                        }),
                    });

                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const data = await response.json();
                    const newName = data.new_name;

                    // Update thread name in the select dropdown
                    renameThreadOption(currentThreadName, newName);
                } catch (error) {
                    console.error('Failed to rename thread:', error);
                }
            }
        };

        const generate = async () => {
            if (!promptInput.value) {
                showNotification("Please enter a prompt.", true);
                return;
            }

            generateBtn.disabled = true;
            stopBtn.disabled = false;

            const userMessage = promptInput.value.replace(/\n/g, '<br>');
            addMessageToChat(userMessage, "user");

            await fetch(API_URL_SEND, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    thread_name: currentThreadName,
                    message: userMessage,
                }),
            });

            promptInput.value = "";

            const response = await fetch(`${API_URL_RECEIVE}/${currentThreadName}?assistant_id=${assistantSelect.value}`);
            const reader = response.body.getReader();
            let output = "";

            while (true) {
                const { done, value } = await reader.read();
                output += new TextDecoder().decode(value);
                let messageElement = document.querySelector('.streaming-message');
                if (!messageElement) {
                    messageElement = document.createElement("div");
                    messageElement.className = `message assistant-message streaming-message`;
                    resultText.appendChild(messageElement);
                }
                messageElement.innerHTML = marked.parse(output);

                if (done) {
                    const streamingMessage = document.querySelector('.streaming-message');
                    if (streamingMessage) {
                        resultText.removeChild(streamingMessage);
                    }

                    messageElement = document.createElement("div");
                    messageElement.className = 'message assistant-message';
                    const regex = /\[.*?\]\((http:\/\/pgpt\.lombello\.com:5000\/messages\/audio\/[a-f0-9-]+\.mp3)\)/g;
                    output = output.replaceAll(regex, '<audio controls src="$1"></audio>');                    
                    messageElement.innerHTML = marked.parse(output);
                    resultText.appendChild(messageElement);
                    scrollToBottom();

                    messageCount += 1;
                    initialMessages.push({role: "assistant", content: output});
                    if (messageCount === 2) {
                        console.log(initialMessages);
                        renameThread(initialMessages);
                    }

                    break;
                }
            }

            generateBtn.disabled = false;
            stopBtn.disabled = true;
        };

        const stop = () => {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
                generateBtn.disabled = false;
                stopBtn.disabled = true;
                resultText.innerText = "Request aborted.";
            }
        };

        if (newChatBtn) {
            newChatBtn.addEventListener("click", initialize);
        }

        if (generateBtn) {
            generateBtn.addEventListener("click", generate);
        }

        if (stopBtn) {
            stopBtn.addEventListener("click", stop);
        }

        if (deleteChatBtn) {
            deleteChatBtn.addEventListener("click", deleteThread);
        }

        promptInput.addEventListener("keyup", (event) => {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                generate();
            }
            if (event.key === "Escape") {
                event.preventDefault();
                stop();
            }
        });

        const loadThreads = async () => {
            const response = await fetch(API_URL_GET_THREADS, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });
            const data = await response.json();
            data.forEach((thread) => {
                addThreadOption({ thread_id: thread.name, chat_name: thread.chat_name });
            });
        };

        const loadAssistants = async () => {
            const response = await fetch(API_URL_LIST_ASSISTANTS, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });
            const data = await response.json();
            data.assistants.forEach((assistant) => {
                const option = document.createElement("option");
                option.value = assistant.id;
                option.text = assistant.name || "Unnamed Assistant";
                assistantSelect.appendChild(option);
            });
        };

        // Fetch updated balance on a regular interval
        setInterval(() => {
            fetch('/')
                .then(response => response.json())
                .then(data => {
                    balanceSpan.textContent = data.balance;
                });
        }, 300000); // Update every 5 minutes

        loadThreads();
        loadAssistants();
        initialize();
    };

    // Fetch the public IP and initialize the application
    fetchPublicIP();
});
