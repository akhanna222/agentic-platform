/**
 * Agentic Platform - Lovable-Style Frontend
 * Modern split-screen interface with real-time updates
 */

// ============================================
// State Management
// ============================================

let selectedAgent = null;
let currentSession = null;
let websocket = null;
let isDarkMode = false;

// ============================================
// Initialize App
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('✨ Agentic Platform UI loaded');

    // Load initial data
    await loadAgents();
    await loadSessions();

    // Initialize theme
    initializeTheme();

    // Setup panel resizer
    setupPanelResizer();
});

// ============================================
// Load Agents
// ============================================

async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();

        const agentsList = document.getElementById('agentsList');
        agentsList.innerHTML = '';

        data.agents.forEach(agent => {
            const item = createAgentItem(agent);
            agentsList.appendChild(item);
        });

        console.log(`✅ Loaded ${data.agents.length} agents`);
    } catch (error) {
        console.error('❌ Failed to load agents:', error);
        showNotification('Failed to load agents', 'error');
    }
}

function createAgentItem(agent) {
    const item = document.createElement('div');
    item.className = 'agent-item';
    item.onclick = () => selectAgent(agent);

    item.innerHTML = `
        <span class="agent-item-icon">${agent.icon}</span>
        <span class="agent-item-name">${agent.name}</span>
    `;

    return item;
}

//============================================
// Select Agent
// ============================================

function selectAgent(agent) {
    selectedAgent = agent;

    // Update sidebar
    document.querySelectorAll('.agent-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');

    // Hide welcome screen, show chat interface
    document.getElementById('welcomeScreen').style.display = 'none';
    document.getElementById('chatInterface').style.display = 'flex';

    // Update chat header
    document.getElementById('chatAgentIcon').textContent = agent.icon;
    document.getElementById('chatAgentName').textContent = agent.name;

    // Clear chat messages
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="system-message">
            <div class="message-icon">${agent.icon}</div>
            <div class="message-content">
                <strong>${agent.name} is ready!</strong>
                <p>${agent.description}</p>
            </div>
        </div>
    `;

    // Focus chat input
    document.getElementById('chatInput').focus();

    console.log(`✅ Selected agent: ${agent.name}`);
}

// ============================================
// Send Message
// ============================================

async function sendMessage() {
    if (!selectedAgent) {
        showNotification('Please select an agent first', 'error');
        return;
    }

    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) {
        showNotification('Please enter a message', 'error');
        return;
    }

    const maxSteps = parseInt(document.getElementById('maxSteps').value);

    // Add user message to chat
    addChatMessage('user', message);

    // Clear input
    chatInput.value = '';

    // Disable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="send-btn-text">Sending...</span>';

    try {
        // Create task session
        const response = await fetch('/api/task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent_type: selectedAgent.id,
                prompt: message,
                max_steps: maxSteps,
            }),
        });

        const data = await response.json();
        currentSession = data.session_id;

        console.log(`✅ Created session: ${currentSession}`);

        // Show output tab
        switchTab('output');

        // Add connecting message
        addOutputMessage('status', 'Connecting to agent...');

        // Connect WebSocket
        connectWebSocket(currentSession);

    } catch (error) {
        console.error('❌ Failed to send message:', error);
        addChatMessage('agent', 'Sorry, I encountered an error. Please try again.');
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span class="send-btn-text">Send</span><span class="send-btn-icon">→</span>';
    }
}

// Handle Enter key in chat input
function handleChatKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// ============================================
// Chat Messages
// ============================================

function addChatMessage(type, content) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `${type}-message`;
    messageDiv.textContent = content;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function clearChat() {
    if (!selectedAgent) return;

    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="system-message">
            <div class="message-icon">${selectedAgent.icon}</div>
            <div class="message-content">
                <strong>Chat cleared!</strong>
                <p>Start a new conversation.</p>
            </div>
        </div>
    `;

    // Clear output
    document.getElementById('outputMessages').innerHTML = '';
    const emptyOutput = document.querySelector('#outputTab .empty-output');
    if (emptyOutput) emptyOutput.style.display = 'block';

    // Reset session
    if (websocket) {
        websocket.close();
        websocket = null;
    }
    currentSession = null;

    // Enable send button
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = false;
    sendBtn.innerHTML = '<span class="send-btn-text">Send</span><span class="send-btn-icon">→</span>';
}

// ============================================
// WebSocket Connection
// ============================================

function connectWebSocket(sessionId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;

    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
        console.log('✅ WebSocket connected');
        addOutputMessage('status', '✅ Connected to agent');
    };

    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        addOutputMessage('error', '❌ Connection error occurred');
    };

    websocket.onclose = () => {
        console.log('🔌 WebSocket closed');

        // Re-enable send button
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span class="send-btn-text">Send</span><span class="send-btn-icon">→</span>';
    };
}

function handleWebSocketMessage(data) {
    console.log('📨 Received:', data.type, data);

    switch (data.type) {
        case 'status':
            addOutputMessage('status', data.message);
            break;

        case 'agent_start':
            addChatMessage('agent', `Processing your request...`);
            addOutputMessage('status', `🤖 ${selectedAgent.name} is working...`);
            break;

        case 'response':
            addChatMessage('agent', data.response);
            addOutputMessage('success', data.response);
            break;

        case 'error':
            addChatMessage('agent', `Error: ${data.message}`);
            addOutputMessage('error', `❌ Error: ${data.message}`);
            break;

        case 'complete':
            addChatMessage('agent', '✅ Task completed!');
            addOutputMessage('success', '✅ Task completed successfully');
            loadSessions(); // Refresh sessions list
            break;

        default:
            console.warn('Unknown message type:', data.type);
    }
}

// ============================================
// Output Messages
// ============================================

function addOutputMessage(type, message) {
    const outputMessages = document.getElementById('outputMessages');
    const emptyOutput = document.querySelector('#outputTab .empty-output');

    // Hide empty state
    if (emptyOutput) {
        emptyOutput.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `output-message ${type}`;
    messageDiv.textContent = message;

    outputMessages.appendChild(messageDiv);
    outputMessages.parentElement.scrollTop = outputMessages.parentElement.scrollHeight;
}

// ============================================
// Tab Switching
// ============================================

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

// ============================================
// Sessions
// ============================================

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();

        const sessionsList = document.getElementById('sessionsList');

        if (data.sessions.length === 0) {
            sessionsList.innerHTML = `
                <div class="empty-state-small">
                    <span class="empty-icon-small">📝</span>
                    <p>No sessions</p>
                </div>
            `;
        } else {
            sessionsList.innerHTML = '';

            // Sort by created_at descending (newest first)
            const sessions = data.sessions
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .slice(0, 10); // Show only last 10

            sessions.forEach(session => {
                const item = createSessionItem(session);
                sessionsList.appendChild(item);
            });
        }

        console.log(`✅ Loaded ${data.sessions.length} sessions`);
    } catch (error) {
        console.error('❌ Failed to load sessions:', error);
    }
}

function createSessionItem(session) {
    const item = document.createElement('div');
    item.className = 'session-item';
    item.onclick = () => viewSession(session.session_id);

    const timeAgo = getTimeAgo(new Date(session.created_at));

    item.innerHTML = `
        <div class="session-item-prompt">${truncate(session.prompt, 40)}</div>
        <div class="session-item-meta">${session.agent_type} • ${timeAgo}</div>
    `;

    return item;
}

async function viewSession(sessionId) {
    try {
        const response = await fetch(`/api/session/${sessionId}`);
        const session = await response.json();

        // Switch to output tab
        switchTab('output');

        // Clear and show session details
        const outputMessages = document.getElementById('outputMessages');
        const emptyOutput = document.querySelector('#outputTab .empty-output');

        if (emptyOutput) {
            emptyOutput.style.display = 'none';
        }

        outputMessages.innerHTML = `
            <div class="output-message status">
                <strong>Session ID:</strong> ${session.session_id}<br>
                <strong>Agent:</strong> ${session.agent_type}<br>
                <strong>Created:</strong> ${new Date(session.created_at).toLocaleString()}<br>
                <strong>Status:</strong> ${session.status}
            </div>
            <div class="output-message">
                <strong>Prompt:</strong><br>
                ${session.prompt}
            </div>
        `;

        if (session.response) {
            outputMessages.innerHTML += `
                <div class="output-message success">
                    <strong>Response:</strong><br>
                    ${session.response}
                </div>
            `;
        }

        if (session.error) {
            outputMessages.innerHTML += `
                <div class="output-message error">
                    <strong>Error:</strong><br>
                    ${session.error}
                </div>
            `;
        }

        console.log(`✅ Loaded session: ${sessionId}`);

    } catch (error) {
        console.error('❌ Failed to load session:', error);
        showNotification('Failed to load session', 'error');
    }
}

// ============================================
// Theme Management
// ============================================

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        enableDarkMode();
    }
}

function toggleTheme() {
    if (isDarkMode) {
        disableDarkMode();
    } else {
        enableDarkMode();
    }
}

function enableDarkMode() {
    document.body.classList.add('dark-mode');
    document.getElementById('themeIcon').textContent = '☀️';
    localStorage.setItem('theme', 'dark');
    isDarkMode = true;
}

function disableDarkMode() {
    document.body.classList.remove('dark-mode');
    document.getElementById('themeIcon').textContent = '🌙';
    localStorage.setItem('theme', 'light');
    isDarkMode = false;
}

function changeTheme(value) {
    if (value === 'dark') {
        enableDarkMode();
    } else if (value === 'light') {
        disableDarkMode();
    } else {
        // System preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            enableDarkMode();
        } else {
            disableDarkMode();
        }
    }
}

// ============================================
// Panel Resizer
// ============================================

function setupPanelResizer() {
    const resizer = document.getElementById('resizer');
    const leftPanel = document.querySelector('.left-panel');
    const rightPanel = document.querySelector('.right-panel');

    let isResizing = false;

    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.body.style.cursor = 'col-resize';
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const containerWidth = document.querySelector('.main-content').offsetWidth;
        const leftWidth = e.clientX - leftPanel.getBoundingClientRect().left;
        const leftPercent = (leftWidth / containerWidth) * 100;

        if (leftPercent > 30 && leftPercent < 70) {
            leftPanel.style.flex = `0 0 ${leftPercent}%`;
            rightPanel.style.flex = `0 0 ${100 - leftPercent}%`;
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = 'default';
        }
    });
}

// ============================================
// Settings Modal
// ============================================

function showSettings() {
    document.getElementById('settingsModal').style.display = 'flex';
}

function closeSettings() {
    document.getElementById('settingsModal').style.display = 'none';
}

// ============================================
// Utility Functions
// ============================================

function showNotification(message, type = 'info') {
    // Simple alert for now - could be improved with toast notifications
    console.log(`[${type.toUpperCase()}] ${message}`);
    if (type === 'error') {
        alert(message);
    }
}

function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

console.log('✅ Agentic Platform initialized');
