(function () {
  'use strict';
  if (window.__AITG_CHATBOT__) return;
  window.__AITG_CHATBOT__ = true;
  var API = window.AITG_CHATBOT_API || '/api/chat';
  var WA = 'https://wa.me/923236715731?text=' + encodeURIComponent('Hello AI Tool Gems, I need help choosing a tool or checking an order.');
  var labels = {
    en: { button: 'AI chat', title: 'AI Tool Gems assistant', intro: 'Ask about current PKR tools, budgets, policies, or guides. I will link sources and avoid guessing.', placeholder: 'Ask in English…', send: 'Send', mic: 'Voice input', stop: 'Stop listening', whatsapp: 'Human WhatsApp support', unavailable: 'Text chat is available if voice is not supported.', loading: 'Checking verified site information…' },
    'roman-ur': { button: 'AI chat', title: 'AI Tool Gems madadgar', intro: 'Current PKR tools, budget, policies ya guides ke baare mein poochein. Main sources share karunga aur guess nahi karunga.', placeholder: 'Roman Urdu mein poochein…', send: 'Bhejein', mic: 'Awaaz input', stop: 'Sunna band karein', whatsapp: 'Human WhatsApp support', unavailable: 'Agar voice support na ho to text chat use karein.', loading: 'Verified site information check ho rahi hai…' },
    ur: { button: 'AI chat', title: 'AI Tool Gems معاون', intro: 'موجودہ PKR ٹولز، بجٹ، پالیسی یا گائیڈز کے بارے میں پوچھیں۔ میں ذرائع دوں گا اور اندازہ نہیں لگاؤں گا۔', placeholder: 'اردو میں پوچھیں…', send: 'بھیجیں', mic: 'آواز ان پٹ', stop: 'سننا بند کریں', whatsapp: 'انسانی WhatsApp مدد', unavailable: 'اگر وائس دستیاب نہ ہو تو ٹیکسٹ چیٹ استعمال کریں۔', loading: 'مصدقہ معلومات چیک ہو رہی ہے…' }
  };
  var language = 'en';
  var root = document.createElement('section');
  root.className = 'aitg-chatbot';
  root.innerHTML = '<button class="aitg-chatbot-launch" type="button" aria-expanded="false" aria-controls="aitg-chatbot-panel">AI chat</button>' +
    '<div class="aitg-chatbot-panel" id="aitg-chatbot-panel" hidden role="dialog" aria-labelledby="aitg-chatbot-title">' +
    '<div class="aitg-chatbot-head"><div><strong id="aitg-chatbot-title">AI Tool Gems assistant</strong><small>Pakistan · PKR · source-based</small></div><button type="button" class="aitg-chatbot-close" aria-label="Close">×</button></div>' +
    '<div class="aitg-chatbot-tools"><label for="aitg-chatbot-language">Language</label><select id="aitg-chatbot-language"><option value="en">English</option><option value="roman-ur">Roman Urdu</option><option value="ur">اردو</option></select></div>' +
    '<div class="aitg-chatbot-messages" aria-live="polite"></div>' +
    '<p class="aitg-chatbot-voice-note"></p>' +
    '<form class="aitg-chatbot-form"><textarea maxlength="800" required rows="2"></textarea><div><button type="button" class="aitg-chatbot-mic">🎙 <span>Voice input</span></button><button type="submit" class="aitg-chatbot-send">Send</button></div></form>' +
    '<a class="aitg-chatbot-wa" target="_blank" rel="noopener nofollow">WhatsApp support</a></div>';
  document.body.appendChild(root);
  var launch = root.querySelector('.aitg-chatbot-launch');
  var panel = root.querySelector('.aitg-chatbot-panel');
  var close = root.querySelector('.aitg-chatbot-close');
  var select = root.querySelector('#aitg-chatbot-language');
  var messages = root.querySelector('.aitg-chatbot-messages');
  var form = root.querySelector('.aitg-chatbot-form');
  var input = form.querySelector('textarea');
  var mic = form.querySelector('.aitg-chatbot-mic');
  var send = form.querySelector('.aitg-chatbot-send');
  var note = root.querySelector('.aitg-chatbot-voice-note');
  root.querySelector('.aitg-chatbot-wa').href = WA;
  function text(key) { return labels[language][key]; }
  function addMessage(content, kind, sources) {
    var item = document.createElement('article'); item.className = 'aitg-chatbot-message ' + kind;
    var body = document.createElement('div'); body.textContent = content; item.appendChild(body);
    if (sources && sources.length) { var list = document.createElement('div'); list.className = 'aitg-chatbot-sources'; sources.slice(0, 5).forEach(function (source) { var link = document.createElement('a'); link.href = source.url; link.target = '_blank'; link.rel = 'noopener'; link.textContent = source.title; list.appendChild(link); }); item.appendChild(list); }
    messages.appendChild(item); messages.scrollTop = messages.scrollHeight;
  }
  function open() { panel.hidden = false; launch.setAttribute('aria-expanded', 'true'); if (!messages.children.length) addMessage(text('intro'), 'bot'); input.focus(); }
  function shut() { panel.hidden = true; launch.setAttribute('aria-expanded', 'false'); launch.focus(); }
  function updateLanguage() { root.setAttribute('lang', language === 'ur' ? 'ur' : language === 'roman-ur' ? 'en-PK' : 'en'); root.setAttribute('dir', language === 'ur' ? 'rtl' : 'ltr'); input.placeholder = text('placeholder'); send.textContent = text('send'); mic.querySelector('span').textContent = text('mic'); note.textContent = text('unavailable'); }
  launch.addEventListener('click', open); close.addEventListener('click', shut); select.addEventListener('change', function () { language = select.value; updateLanguage(); });
  form.addEventListener('submit', async function (event) { event.preventDefault(); var message = input.value.trim(); if (!message) return; addMessage(message, 'user'); input.value = ''; send.disabled = true; mic.disabled = true; addMessage(text('loading'), 'bot loading'); try { var response = await fetch(API, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ message: message, language: language, page: location.pathname }) }); var data = await response.json(); var pending = messages.querySelector('.loading:last-child'); if (pending) pending.remove(); if (!response.ok || !data.answer) throw new Error('chat unavailable'); addMessage(data.answer, 'bot', data.sources); } catch (error) { var pendingError = messages.querySelector('.loading:last-child'); if (pendingError) pendingError.remove(); addMessage('I could not reach the chat service. I will not guess. Please use WhatsApp support for current product or order help.', 'bot', [{ title: 'WhatsApp support', url: WA }]); } finally { send.disabled = false; mic.disabled = false; input.focus(); } });
  var Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) { mic.disabled = true; note.textContent = text('unavailable'); } else { var recognition = new Recognition(); recognition.interimResults = false; recognition.maxAlternatives = 1; recognition.onstart = function () { mic.classList.add('listening'); mic.querySelector('span').textContent = text('stop'); }; recognition.onend = function () { mic.classList.remove('listening'); mic.querySelector('span').textContent = text('mic'); }; recognition.onerror = function () { note.textContent = text('unavailable'); }; recognition.onresult = function (event) { input.value = event.results[0][0].transcript; input.focus(); }; mic.addEventListener('click', function () { recognition.lang = language === 'ur' ? 'ur-PK' : language === 'roman-ur' ? 'en-PK' : 'en-US'; try { recognition.start(); } catch (error) { recognition.stop(); } }); }
  updateLanguage();
}());
