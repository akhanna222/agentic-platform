/**
 * Agentic Platform - Frontend JavaScript
 * Handles agent selection, task execution, and real-time updates
 */

// State management
let selectedAgent = null;
let currentSession = null;
let websocket = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Agentic Platform UI loaded');
    await loadAgents();
    await loadSessions();
});

/**
 * Load available agents from API
 */
async function loadAgents() {
    try {
        const response = await fetch('/api/agents');
        const data = await response.json();

        const grid = document.getElementById('agentsGrid');
        grid.innerHTML = '';

        data.agents.forEach(agent => {
            const card = createAgentCard(agent);
            grid.appendChild(card);
        });

        console.log(`✅ Loaded ${data.agents.length} agents`);
    } catch (error) {
        console.error('❌ Failed to load agents:', error);
        showError('Failed to load agents. Please refresh the page.');
    }
}

/**
 * Create an agent card element
 */
function createAgentCard(agent) {
    const card = document.createElement('div');
    card.className = 'agent-card';
    card.onclick = () => selectAgent(agent);

    card.innerHTML = `
        <span class="agent-icon">${agent.icon}</span>
        <h3 class="agent-name">${agent.name}</h3>
        <p class="agent-description">${agent.description}</p>
    `;

    return card;
}

/**
 * Select an agent
 */
function selectAgent(agent) {
    selectedAgent = agent;

    // Update UI
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');

    // Show task section
    document.getElementById('taskSection').style.display = 'block';

    // Update selected agent info
    document.getElementById('selectedAgentIcon').textContent = agent.icon;
    document.getElementById('selectedAgentName').textContent = agent.name;
    document.getElementById('selectedAgentDesc').textContent = agent.description;

    // Scroll to task section
    document.getElementById('taskSection').scrollIntoView({ behavior: 'smooth' });

    console.log(`✅ Selected agent: ${agent.name}`);
}

/**
 * Change the selected agent
 */
function changeAgent() {
    selectedAgent = null;
    document.querySelectorAll('.agent-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.getElementById('taskSection').style.display = 'none';

    // Scroll back to agents
    document.querySelector('.agents-section').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Start a new task
 */
async function startTask() {
    if (!selectedAgent) {
        showError('Please select an agent first');
        return;
    }

    const prompt = document.getElementById('taskPrompt').value.trim();
    if (!prompt) {
        showError('Please enter a task description');
        return;
    }

    const maxSteps = parseInt(document.getElementById('maxSteps').value);

    // Disable start button
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = true;
    startBtn.innerHTML = '<span>⏳ Starting...</span>';

    try {
        // Create task session
        const response = await fetch('/api/task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent_type: selectedAgent.id,
                prompt: prompt,
                max_steps: maxSteps,
            }),
        });

        const data = await response.json();
        currentSession = data.session_id;

        console.log(`✅ Created session: ${currentSession}`);

        // Show output section
        document.getElementById('outputSection').style.display = 'block';
        document.getElementById('outputContent').innerHTML = '';
        document.getElementById('statusBadge').textContent = 'Connecting...';
        document.getElementById('statusBadge').className = 'status-badge running';

        // Scroll to output
        document.getElementById('outputSection').scrollIntoView({ behavior: 'smooth' });

        // Connect WebSocket
        connectWebSocket(currentSession);

    } catch (error) {
        console.error('❌ Failed to start task:', error);
        showError('Failed to start task. Please try again.');
        startBtn.disabled = false;
        startBtn.innerHTML = '<span>🚀 Start Building</span>';
    }
}

/**
 * Connect to WebSocket for real-time updates
 */
function connectWebSocket(sessionId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;

    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);

    websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
        console.log('✅ WebSocket connected');
        addOutputMessage('status', 'Connected to agent...');
    };

    websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    websocket.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        addOutputMessage('error', 'Connection error occurred');
    };

    websocket.onclose = () => {
        console.log('🔌 WebSocket closed');
    };
}

/**
 * Handle WebSocket messages
 */
function handleWebSocketMessage(data) {
    console.log('📨 Received:', data.type, data);

    switch (data.type) {
        case 'status':
            updateStatus(data.status, data.message);
            addOutputMessage('status', data.message);
            break;

        case 'agent_start':
            addOutputMessage('status', `🤖 ${selectedAgent.name} is processing your request...`);
            break;

        case 'response':
            addOutputMessage('response', data.response);
            updateStats(data.steps_used, data.max_steps, data.state);
            break;

        case 'error':
            addOutputMessage('error', `Error: ${data.message}`);
            updateStatus('error', 'Task failed');
            showTaskComplete();
            break;

        case 'complete':
            updateStatus('completed', 'Task completed');
            showTaskComplete();
            loadSessions(); // Refresh sessions list
            break;

        default:
            console.warn('Unknown message type:', data.type);
    }
}

/**
 * Add a message to the output
 */
function addOutputMessage(type, message) {
    const outputContent = document.getElementById('outputContent');

    const messageDiv = document.createElement('div');
    messageDiv.className = `output-message ${type}`;
    messageDiv.textContent = message;

    outputContent.appendChild(messageDiv);

    // Auto-scroll to bottom
    outputContent.scrollTop = outputContent.scrollHeight;
}

/**
 * Update status badge
 */
function updateStatus(status, message) {
    const badge = document.getElementById('statusBadge');
    badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    badge.className = `status-badge ${status}`;
}

/**
 * Update stats in footer
 */
function updateStats(stepsUsed, maxSteps, state) {
    document.getElementById('stepsUsed').textContent = `Steps: ${stepsUsed}/${maxSteps}`;
    document.getElementById('agentState').textContent = `State: ${state}`;
    document.getElementById('outputFooter').style.display = 'flex';
}

/**
 * Show task complete state
 */
function showTaskComplete() {
    const startBtn = document.getElementById('startBtn');
    startBtn.disabled = false;
    startBtn.innerHTML = '<span>🚀 Start Building</span>';

    // Close WebSocket
    if (websocket) {
        websocket.close();
        websocket = null;
    }
}

/**
 * Stop the current task
 */
function stopTask() {
    if (websocket) {
        websocket.close();
        websocket = null;
    }

    addOutputMessage('status', '⏹ Task stopped by user');
    updateStatus('completed', 'Stopped');
    showTaskComplete();
}

/**
 * Reset and start a new task
 */
function resetTask() {
    // Clear output
    document.getElementById('outputContent').innerHTML = '';
    document.getElementById('outputFooter').style.display = 'none';
    document.getElementById('outputSection').style.display = 'none';

    // Clear input
    document.getElementById('taskPrompt').value = '';

    // Reset state
    currentSession = null;

    // Scroll back to task input
    document.getElementById('taskSection').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Load recent sessions
 */
async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const data = await response.json();

        const sessionsList = document.getElementById('sessionsList');

        if (data.sessions.length === 0) {
            sessionsList.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">📝</span>
                    <p>No sessions yet. Start a task to begin!</p>
                </div>
            `;
        } else {
            sessionsList.innerHTML = '';

            // Sort by created_at descending
            const sessions = data.sessions.sort((a, b) =>
                new Date(b.created_at) - new Date(a.created_at)
            );

            sessions.forEach(session => {
                const card = createSessionCard(session);
                sessionsList.appendChild(card);
            });
        }

        console.log(`✅ Loaded ${data.sessions.length} sessions`);
    } catch (error) {
        console.error('❌ Failed to load sessions:', error);
    }
}

/**
 * Create a session card element
 */
function createSessionCard(session) {
    const card = document.createElement('div');
    card.className = 'session-card';

    const date = new Date(session.created_at);
    const timeAgo = getTimeAgo(date);

    card.innerHTML = `
        <div class="session-info">
            <div class="session-prompt">${truncate(session.prompt, 60)}</div>
            <div class="session-meta">
                ${session.agent_type} • ${session.status} • ${timeAgo}
            </div>
        </div>
        <button class="btn-secondary" onclick="viewSession('${session.session_id}')">
            View
        </button>
    `;

    return card;
}

/**
 * View a session
 */
async function viewSession(sessionId) {
    try {
        const response = await fetch(`/api/session/${sessionId}`);
        const session = await response.json();

        // Show session details in output section
        document.getElementById('outputSection').style.display = 'block';
        document.getElementById('statusBadge').textContent = session.status;
        document.getElementById('statusBadge').className = `status-badge ${session.status}`;

        const outputContent = document.getElementById('outputContent');
        outputContent.innerHTML = `
            <div class="output-message status">
                <strong>Session:</strong> ${session.session_id}<br>
                <strong>Agent:</strong> ${session.agent_type}<br>
                <strong>Created:</strong> ${new Date(session.created_at).toLocaleString()}<br>
                <strong>Status:</strong> ${session.status}
            </div>
            <div class="output-message response">
                <strong>Prompt:</strong><br>
                ${session.prompt}
            </div>
        `;

        if (session.response) {
            outputContent.innerHTML += `
                <div class="output-message response">
                    <strong>Response:</strong><br>
                    ${session.response}
                </div>
            `;
        }

        if (session.error) {
            outputContent.innerHTML += `
                <div class="output-message error">
                    <strong>Error:</strong><br>
                    ${session.error}
                </div>
            `;
        }

        document.getElementById('outputSection').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('❌ Failed to load session:', error);
        showError('Failed to load session details');
    }
}

/**
 * Show the about modal
 */
function showAbout() {
    document.getElementById('aboutModal').style.display = 'flex';
}

/**
 * Close the about modal
 */
function closeAbout() {
    document.getElementById('aboutModal').style.display = 'none';
}

// Close modal when clicking outside
document.addEventListener('click', (event) => {
    const modal = document.getElementById('aboutModal');
    if (event.target === modal) {
        closeAbout();
    }
});

/**
 * Utility: Show error message
 */
function showError(message) {
    alert(message); // Simple for now, could be improved with toast notifications
}

/**
 * Utility: Truncate text
 */
function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}

/**
 * Utility: Get time ago string
 */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
}

console.log('✅ Agentic Platform UI initialized');
