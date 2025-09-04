from typing import Any, Dict, Optional

from django import forms

# نحاول استيراد الموديلات؛ ولو غير متوفرة نعرّف بدائل آمنة تمنع كسر الاستيراد
try:
    from .models import SupportResponse as _SupportResponse  # type: ignore
except Exception:  # pragma: no cover
    _SupportResponse = None  # type: ignore[assignment]

try:
    from .models import SupportTicket as _SupportTicket  # type: ignore
except Exception:  # pragma: no cover
    _SupportTicket = None  # type: ignore[assignment]

# =========================
# تذاكر الدعم
# =========================
if _SupportTicket is not None:
    class SupportTicketForm(forms.ModelForm):  # type: ignore[misc]
        class Meta:
            model = _SupportTicket
            # نفترض وجود حقل client ونستبعده ليُضبط في الـ view
            exclude = ("client",)
            # إن لم يكن الحقل موجودًا فلن تؤثر الاستثناءات على صحة النموذج
else:
    class SupportTicketForm(forms.Form):  # Fallback لا يكسر الاستيراد
        # حقول بديلة غير مُستخدمة فعليًا عند تعطيل موديل الدعم
        subject = forms.CharField(required=False)
        description = forms.CharField(widget=forms.Textarea, required=False)

        def save(self, commit: bool = False) -> Any:  # pragma: no cover
            # لن تُستدعى عمليًا لأن الـ views تتحقق من توافر الموديل
            raise RuntimeError("SupportTicket model is not available.")

# =========================
# ردود الدعم
# =========================
if _SupportResponse is not None:
    class SupportResponseForm(forms.ModelForm):  # type: ignore[misc]
        class Meta:
            model = _SupportResponse
            # نفترض ربط الرد بالتذكرة والمُجيب من الـ view
            exclude = ("ticket", "responder")
else:
    class SupportResponseForm(forms.Form):  # Fallback لا يكسر الاستيراد
        message = forms.CharField(widget=forms.Textarea, required=False)

        def save(self, commit: bool = False) -> Any:  # pragma: no cover
            raise RuntimeError("SupportResponse model is not available.")
