import logging

logger = logging.getLogger('sherpa')

SUSPICIOUS_PHRASES = [
    'kontonummer',
    'million',
    'dollar',
    'lovepedia',
]

def parse_for_spam(request, name, email, text, annonse):
    lowercase_text = text.lower()
    if any([phrase.lower() in lowercase_text for phrase in SUSPICIOUS_PHRASES]):
        logger.warning(u"Mistenkelig Fjelltreffen-svar",
            extra={
                'request': request,
                'sender_name': name,
                'email': email,
                'text': text,
                'annonse': annonse,
            }
        )
