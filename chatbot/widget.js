(function () {
  'use strict';
  if (window.__AITG_CHATBOT__) return;
  window.__AITG_CHATBOT__ = true;

  var API = window.AITG_CHATBOT_API || 'https://aitoolgems-chatbot.mrehmanfarooq6.workers.dev/api/chat';
  var WA = 'https://wa.me/923236715731?text=' + encodeURIComponent('Hello AI Tool Gems, I need help choosing a tool or checking an order.');
  var REQUEST_TIMEOUT = 20000;
  var labels = {
    en: { button: 'AI chat', title: 'AI Tool Gems assistant', intro: 'Ask about current PKR tools, budgets, policies, or guides. I will link sources and avoid guessing.', placeholder: 'Ask in English…', send: 'Send', mic: 'Voice input', stop: 'Stop listening', whatsapp: 'Human WhatsApp support', unavailable: 'Text chat is available if voice is not supported.', loading: 'Checking verified site information…', newChat: 'New chat', quick: 'Quick questions', minimize: 'Minimize chat', close: 'Close chat', retry: 'Retry' },
    'roman-ur': { button: 'AI chat', title: 'AI Tool Gems madadgar', intro: 'Current PKR tools, budget, policies ya guides ke baare mein poochein. Main sources share karunga aur guess nahi karunga.', placeholder: 'Roman Urdu mein poochein…', send: 'Bhejein', mic: 'Awaaz input', stop: 'Sunna band karein', whatsapp: 'Human WhatsApp support', unavailable: 'Agar voice support na ho to text chat use karein.', loading: 'Verified site information check ho rahi hai…', newChat: 'Nayi chat', quick: 'Jaldi sawalat', minimize: 'Chat chhoti karein', close: 'Chat band karein', retry: 'Dobara koshish' },
    ur: { button: 'AI chat', title: 'AI Tool Gems معاون', intro: 'موجودہ PKR ٹولز، بجٹ، پالیسی یا گائیڈز کے بارے میں پوچھیں۔ میں ذرائع دوں گا اور اندازہ نہیں لگاؤں گا۔', placeholder: 'اردو میں پوچھیں…', send: 'بھیجیں', mic: 'آواز ان پٹ', stop: 'سننا بند کریں', whatsapp: 'انسانی WhatsApp مدد', unavailable: 'اگر وائس دستیاب نہ ہو تو ٹیکسٹ چیٹ استعمال کریں۔', loading: 'مصدقہ معلومات چیک ہو رہی ہیں…', newChat: 'نئی چیٹ', quick: 'فوری سوالات', minimize: 'چیٹ چھوٹی کریں', close: 'چیٹ بند کریں', retry: 'دوبارہ کوشش' }
  };
  var quickPrompts = {
    en: ['Find a product under Rs. 1,000', 'Compare ChatGPT and Gemini', 'Explain the refund policy', 'Help me place an order'],
    'roman-ur': ['Rs. 1,000 ke andar tool dhoondho', 'ChatGPT aur Gemini compare karo', 'Refund policy samjhao', 'Order place karne mein madad'],
    ur: ['Rs. 1,000 سے کم ٹول تلاش کریں', 'ChatGPT اور Gemini کا موازنہ کریں', 'ریفنڈ پالیسی سمجھائیں', 'آرڈر کرنے میں مدد کریں']
  };
  var language = 'en';
  var history = [];
  var state = 'closed';
  var requestSerial = 0;
  var activeRequest = null;
  var lastFailedMessage = '';

  var root = document.createElement('section');
  root.className = 'aitg-chatbot';
  root.innerHTML = '<button class="aitg-chatbot-launch" type="button" aria-expanded="false" aria-controls="aitg-chatbot-panel">AI chat</button>' +
    '<div class="aitg-chatbot-panel" id="aitg-chatbot-panel" hidden role="dialog" aria-modal="false" aria-labelledby="aitg-chatbot-title">' +
    '<div class="aitg-chatbot-head"><div><strong id="aitg-chatbot-title">AI Tool Gems assistant</strong><small>Pakistan · PKR · source-based</small></div><div class="aitg-chatbot-head-actions"><button type="button" class="aitg-chatbot-minimize" aria-label="Minimize chat">−</button><button type="button" class="aitg-chatbot-close" aria-label="Close chat">×</button></div></div>' +
    '<div class="aitg-chatbot-tools"><label for="aitg-chatbot-language">Language</label><select id="aitg-chatbot-language"><option value="en">English</option><option value="roman-ur">Roman Urdu</option><option value="ur">اردو</option></select><button type="button" class="aitg-chatbot-new">New chat</button></div>' +
    '<div class="aitg-chatbot-quick" aria-label="Quick questions"><span></span><div class="aitg-chatbot-quick-list"></div></div>' +
    '<div class="aitg-chatbot-messages" aria-live="polite"></div>' +
    '<p class="aitg-chatbot-voice-note"></p>' +
    '<form class="aitg-chatbot-form"><textarea maxlength="800" required rows="2"></textarea><div><button type="button" class="aitg-chatbot-mic">🎙 <span>Voice input</span></button><button type="submit" class="aitg-chatbot-send">Send</button></div></form>' +
    '<a class="aitg-chatbot-wa" target="_blank" rel="noopener nofollow">WhatsApp support</a></div>';
  document.body.appendChild(root);

  var launch = root.querySelector('.aitg-chatbot-launch');
  var panel = root.querySelector('.aitg-chatbot-panel');
  var close = root.querySelector('.aitg-chatbot-close');
  var minimize = root.querySelector('.aitg-chatbot-minimize');
  var select = root.querySelector('#aitg-chatbot-language');
  var newChat = root.querySelector('.aitg-chatbot-new');
  var messages = root.querySelector('.aitg-chatbot-messages');
  var quickLabel = root.querySelector('.aitg-chatbot-quick span');
  var quickList = root.querySelector('.aitg-chatbot-quick-list');
  var form = root.querySelector('.aitg-chatbot-form');
  var input = form.querySelector('textarea');
  var mic = form.querySelector('.aitg-chatbot-mic');
  var send = form.querySelector('.aitg-chatbot-send');
  var note = root.querySelector('.aitg-chatbot-voice-note');
  var headActions = root.querySelector('.aitg-chatbot-head-actions');
  root.querySelector('.aitg-chatbot-wa').href = WA;

  function text(key) { return labels[language][key]; }
  function track(name) { if (typeof window.gtag === 'function') window.gtag('event', name, { event_category: 'chatbot' }); }
  function safeSource(source) { return source && typeof source.url === 'string' && /^(https?:\/\/|\/)/i.test(source.url); }
  function addMessage(content, kind, sources, retryMessage) {
    var item = document.createElement('article'); item.className = 'aitg-chatbot-message ' + kind;
    var body = document.createElement('div'); body.textContent = content; item.appendChild(body);
    if (sources && sources.length) {
      var list = document.createElement('div'); list.className = 'aitg-chatbot-sources';
      sources.slice(0, 5).filter(safeSource).forEach(function (source) { var link = document.createElement('a'); link.href = source.url; link.target = '_blank'; link.rel = 'noopener'; link.textContent = source.title || 'Source'; link.addEventListener('click', function () { track('chatbot_source_click'); }); list.appendChild(link); });
      item.appendChild(list);
    }
    if (retryMessage) { var retry = document.createElement('button'); retry.type = 'button'; retry.className = 'aitg-chatbot-retry'; retry.textContent = text('retry'); retry.addEventListener('click', function () { item.remove(); submitMessage(retryMessage); }); item.appendChild(retry); }
    messages.appendChild(item); messages.scrollTop = messages.scrollHeight;
  }
  function renderQuickPrompts() {
    quickLabel.textContent = text('quick'); quickList.replaceChildren();
    quickPrompts[language].forEach(function (prompt) { var button = document.createElement('button'); button.type = 'button'; button.textContent = prompt; button.addEventListener('click', function () { input.value = prompt; input.focus(); }); quickList.appendChild(button); });
  }
  function setPanel(nextState) {
    state = nextState;
    panel.hidden = nextState === 'closed' || nextState === 'minimized';
    launch.setAttribute('aria-expanded', panel.hidden ? 'false' : 'true');
    root.dataset.state = nextState;
    if (!panel.hidden) input.focus();
  }
  function open() { setPanel('open'); if (!messages.children.length) addMessage(text('intro'), 'bot'); }
  function minimizeChat() { setPanel('minimized'); }
  function shut() { setPanel('closed'); }
  function clearChat() { requestSerial += 1; if (activeRequest) activeRequest.abort(); activeRequest = null; history = []; lastFailedMessage = ''; messages.replaceChildren(); setPanel('open'); addMessage(text('intro'), 'bot'); track('chatbot_new_conversation'); }
  function updateLanguage() { root.setAttribute('lang', language === 'ur' ? 'ur' : language === 'roman-ur' ? 'en-PK' : 'en'); root.setAttribute('dir', language === 'ur' ? 'rtl' : 'ltr'); input.placeholder = text('placeholder'); send.textContent = text('send'); mic.querySelector('span').textContent = text('mic'); note.textContent = text('unavailable'); newChat.textContent = text('newChat'); minimize.setAttribute('aria-label', text('minimize')); close.setAttribute('aria-label', text('close')); renderQuickPrompts(); }
  function finishRequest(serial) { if (serial === requestSerial) { activeRequest = null; send.disabled = false; mic.disabled = false; form.removeAttribute('aria-busy'); } }
  async function submitMessage(message) {
    if (!message || activeRequest) return;
    addMessage(message, 'user'); history.push({ role: 'user', content: message }); history = history.slice(-6); input.value = ''; send.disabled = true; mic.disabled = true; form.setAttribute('aria-busy', 'true'); addMessage(text('loading'), 'bot loading');
    var serial = ++requestSerial; var controller = typeof AbortController === 'function' ? new AbortController() : null; activeRequest = controller || { abort: function () {} };
    var timer = controller ? window.setTimeout(function () { controller.abort(); }, REQUEST_TIMEOUT) : null;
    try {
      var response = await fetch(API, { method: 'POST', headers: { 'content-type': 'application/json' }, signal: controller ? controller.signal : undefined, body: JSON.stringify({ message: message, language: language, page: location.pathname, history: history }) });
      var raw = await response.text(); var data;
      try { data = raw ? JSON.parse(raw) : null; } catch (parseError) { throw new Error('invalid response'); }
      var pending = messages.querySelector('.loading:last-child'); if (pending) pending.remove();
      if (!response.ok || !data || typeof data.answer !== 'string' || !data.answer.trim()) throw new Error('chat unavailable');
      if (serial !== requestSerial) return;
      lastFailedMessage = ''; addMessage(data.answer, 'bot', data.sources); history.push({ role: 'assistant', content: data.answer.slice(0, 600) }); history = history.slice(-6); track(data.sources && data.sources.length ? 'chatbot_answer' : 'chatbot_answer_unavailable');
    } catch (error) {
      var pendingError = messages.querySelector('.loading:last-child'); if (pendingError) pendingError.remove();
      if (serial !== requestSerial) return;
      lastFailedMessage = message; addMessage('I could not reach the chat service. I will not guess. Please try again or use WhatsApp support.', 'bot error', [{ title: 'WhatsApp support', url: WA }], message); track('chatbot_answer_unavailable');
    } finally { if (timer) window.clearTimeout(timer); finishRequest(serial); if (state === 'open') input.focus(); }
  }

  launch.addEventListener('click', open); close.addEventListener('click', shut); minimize.addEventListener('click', minimizeChat); newChat.addEventListener('click', clearChat); select.addEventListener('change', function () { language = select.value; updateLanguage(); });
  headActions.addEventListener('click', function (eventObject) { eventObject.stopPropagation(); });
  root.querySelector('.aitg-chatbot-wa').addEventListener('click', function () { track('chatbot_whatsapp_click'); });
  form.addEventListener('keydown', function (eventObject) { if (eventObject.key === 'Enter' && !eventObject.shiftKey) { eventObject.preventDefault(); form.requestSubmit(); } });
  form.addEventListener('submit', function (eventObject) { eventObject.preventDefault(); submitMessage(input.value.trim()); });

  var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) { mic.disabled = true; note.textContent = text('unavailable'); } else {
    var recognition = new Recognition(); recognition.interimResults = false; recognition.maxAlternatives = 1;
    recognition.onstart = function () { mic.classList.add('listening'); mic.querySelector('span').textContent = text('stop'); };
    recognition.onend = function () { mic.classList.remove('listening'); mic.querySelector('span').textContent = text('mic'); };
    recognition.onerror = function () { note.textContent = text('unavailable'); };
    recognition.onresult = function (eventObject) { input.value = eventObject.results[0][0].transcript; input.focus(); };
    mic.addEventListener('click', function () { recognition.lang = language === 'ur' ? 'ur-PK' : language === 'roman-ur' ? 'en-PK' : 'en-US'; try { recognition.start(); } catch (error) { recognition.stop(); } });
  }
  updateLanguage();
}());
