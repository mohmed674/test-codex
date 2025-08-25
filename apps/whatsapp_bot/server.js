const axios = require('axios');

sock.ev.on('messages.upsert', async ({ messages }) => {
  const msg = messages[0];
  if (!msg.message) return;

  const sender = msg.key.remoteJid;
  const text = msg.message.conversation || msg.message.extendedTextMessage?.text || '';

  // إرسال الرسالة إلى Django لتحليلها والرد
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/receive_whatsapp_message/', {
      sender: sender,
      message: text
    });
    const reply = response.data.reply;
    await sock.sendMessage(sender, { text: reply });
  } catch (error) {
    console.error("خطأ أثناء إرسال الرسالة إلى Django:", error);
  }
});
