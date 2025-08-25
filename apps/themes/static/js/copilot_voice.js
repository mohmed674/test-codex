// static/js/copilot_voice.js - أوامر صوتية لمساعد ERP

// ✅ التأكد من دعم المتصفح لـ Web Speech API
if ('webkitSpeechRecognition' in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.lang = 'ar-EG';
  recognition.continuous = false;
  recognition.interimResults = false;

  const micBtn = document.createElement("button");
  micBtn.textContent = "🎤 تحدث";
  micBtn.style = "background:#dc3545;color:white;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;margin:20px auto;display:block";
  document.querySelector('.copilot-container').prepend(micBtn);

  micBtn.onclick = () => recognition.start();

  recognition.onresult = function (event) {
    const voiceQuery = event.results[0][0].transcript;
    console.log("✅ صوت مسموع:", voiceQuery);

    // إرسال الطلب باستخدام HTMX
    const responseBox = document.getElementById("response");
    fetch(`/copilot/query/?query=${encodeURIComponent(voiceQuery)}`)
      .then(res => res.text())
      .then(html => responseBox.innerHTML = html);
  };

  recognition.onerror = function (event) {
    alert("⚠️ حدث خطأ في التعرف الصوتي: " + event.error);
  };

} else {
  console.warn("🎙️ متصفحك لا يدعم Web Speech API.");
}
