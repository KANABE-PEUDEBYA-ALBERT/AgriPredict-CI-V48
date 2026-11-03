import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from assistant_service import (
    ask_gemini, build_prompt, validate_question, _extract_text, _model_chain,
)


class AssistantServiceTests(unittest.TestCase):
    def test_question_validation(self):
        self.assertEqual(validate_question("  Bonjour ?  "), "Bonjour ?")
        self.assertEqual(validate_question("x" * 12000), "x" * 12000)
        with self.assertRaises(ValueError):
            validate_question("   ")

    def test_prompt_contains_only_supplied_context(self):
        prompt = build_prompt(product="Riz", guide={"etapes": ["semis"]}, plots="Parcelle A, 2 ha", prices="Aucun prix")
        self.assertIn("Parcelle A, 2 ha", prompt)
        self.assertIn("Aucun prix", prompt)
        self.assertIn("N'invente jamais", prompt)
        self.assertIn("Ne prescris aucune marque", prompt)

    def test_missing_key_is_reported(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_NOT_CONFIGURED"):
                ask_gemini("question", "prompt")

    def test_model_chain_puts_env_model_first_without_duplicates(self):
        with patch.dict(os.environ, {"GEMINI_MODEL": "gemini-3.7-flash"}):
            self.assertEqual(_model_chain(), ["gemini-3.7-flash", "gemini-3.5-flash-lite"])

    def test_extract_text(self):
        ok, text = _extract_text(SimpleNamespace(text="  Réponse utile  "))
        self.assertTrue(ok)
        self.assertEqual(text, "Réponse utile")


if __name__ == "__main__":
    unittest.main()
