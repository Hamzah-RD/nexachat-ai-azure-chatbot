const chat = document.querySelector('#chat');
const form = document.querySelector('#form');
const input = document.querySelector('#input');
const send = document.querySelector('#send');
const clear = document.querySelector('#clear');
const status = document.querySelector('#status');
const welcome = document.querySelector('#welcome');
let history = [];
let busy = false;
function bubble(role, content) {
  welcome.hidden = true;
  const article = document.createElement('article');
  article.className = role;
  const label = document.createElement('b');
  label.textContent = role === 'user' ? 'YOU' : 'HAMZAH RD AI';
  const text = document.createElement('div');
  text.dir = 'auto';
  text.textContent = content;
  article.append(label, text); chat.append(article);
  chat.scrollTop = chat.scrollHeight;
  return article;
}
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const content = input.value.trim();
  if (!content || busy) return;
  busy = true; send.disabled = true; clear.disabled = true;
  input.value = ''; status.textContent = 'Thinking…';
  const userBubble = bubble('user', content);
  const messages = [...history.slice(-20), {role: 'user', content}];
  try {
    const response = await fetch('/api/chat', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({messages}), signal: AbortSignal.timeout(90000)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed. Try again.');
    bubble('assistant', data.reply);
    history = [...messages, {role: 'assistant', content: data.reply}];
    status.textContent = '';
  } catch (error) {
    userBubble.remove(); input.value = content;
    status.textContent = error.name === 'TimeoutError' ? 'Request timed out. Please retry.' : error.message;
    if (!history.length) welcome.hidden = false;
  } finally {
    busy = false; send.disabled = false; clear.disabled = false; input.focus();
  }
});
clear.addEventListener('click', () => {
  if (busy) return;
  history = []; chat.querySelectorAll('article').forEach(x => x.remove());
  welcome.hidden = false; status.textContent = ''; input.value = ''; input.focus();
});
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault(); form.requestSubmit();
  }
});
document.querySelectorAll('[data-prompt]').forEach(button => button.addEventListener('click', () => {
  input.value = button.dataset.prompt; form.requestSubmit();
}));
