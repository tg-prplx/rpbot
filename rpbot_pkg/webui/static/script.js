const userId = Math.floor(Math.random()*1e9);
const messagesDiv = document.getElementById('messages');
const input = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(text, author) {
  const div = document.createElement('div');
  div.className = 'message ' + author;
  div.textContent = text;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  return div;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, 'user');
  input.value = '';
  const loadingDiv = addMessage('...', 'bot');
  const resp = await fetch(`/api/chat/${userId}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message:text})
  });
  const data = await resp.json();
  loadingDiv.textContent = data.response;
}

sendBtn.addEventListener('click', sendMessage);
input.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
