import json
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from flask import current_app
from flask_babel import _


def translate(text, source_language, dest_language):
    if 'LANGUAGE_TRANSLATOR_APIKEY' not in current_app.config or \
            not current_app.config['LANGUAGE_TRANSLATOR_APIKEY']:
        return _("Erreur : le service de traduction n'est pas configuré.")
    authenticator = IAMAuthenticator(current_app.config['LANGUAGE_TRANSLATOR_APIKEY'])
    language_translator = LanguageTranslatorV3(
        version='2021-09-23',
        authenticator=authenticator
    )
    response = language_translator.translate(
            text=text,
            source=source_language, target=dest_language)
    if response.get_status_code() != 200:
        return _("Erreur : la traduction a échoué")
    translation_result = json.dumps(response.get_result(), indent=2, ensure_ascii=False)
    return json.loads(translation_result)['translations'][0]['translation']
