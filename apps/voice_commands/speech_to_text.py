import speech_recognition as sr
from pydub import AudioSegment
import os
import tempfile

def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()

    # إنشاء ملف WAV مؤقت من ملف الصوت المرفوع
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        audio = AudioSegment.from_file(audio_file)
        audio.export(temp_file.name, format="wav")
        temp_file_path = temp_file.name

    # محاولة التعرف على النص
    try:
        with sr.AudioFile(temp_file_path) as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_google(audio_data, language="ar-EG")
    except sr.UnknownValueError:
        transcript = "❌ لم يتم التعرف على محتوى الصوت"
    except sr.RequestError:
        transcript = "⚠️ تعذر الاتصال بخدمة التعرف الصوتي"
    finally:
        os.remove(temp_file_path)  # حذف الملف المؤقت

    return transcript
