import unittest
from unittest.mock import ANY, call, patch

from prompt_toolkit.completion.base import CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from InquirerPy.base import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.prompts.input import InputPrompt


class TestInputPrompt(unittest.TestCase):
    def setUp(self):
        self.inp = create_pipe_input()

    def tearDown(self):
        self.inp.close()

    def test_prompt_result(self):
        self.inp.send_text("hello\n")
        input_prompt = InputPrompt(
            message="yes",
            style={},
            default="world",
            symbol="!",
            editing_mode="emacs",
            input=self.inp,
            output=DummyOutput(),
        )
        result = input_prompt.execute()
        self.assertEqual(result, "worldhello")
        self.assertEqual(
            input_prompt.status, {"answered": True, "result": "worldhello"}
        )

    def test_prompt_result_multiline(self):
        self.inp.send_text("hello\nworld\nfoo\nboo\x1b\r")
        input_prompt = InputPrompt(
            message="yes",
            style={},
            default="",
            symbol="!",
            editing_mode="emacs",
            input=self.inp,
            output=DummyOutput(),
            multiline=True,
        )
        result = input_prompt.execute()
        self.assertEqual(result, "hello\nworld\nfoo\nboo")
        self.assertEqual(
            input_prompt.status, {"answered": True, "result": "hello\nworld\nfoo\nboo"}
        )

    def test_prompt_completion(self):
        input_prompt = InputPrompt(
            message="yes",
            style={},
            default="",
            symbol="!",
            editing_mode="emacs",
            input=self.inp,
            output=DummyOutput(),
            multiline=True,
            completer={"hello": None, "hey": None, "what": None},
        )

        completer = input_prompt.completer
        doc_text = "he"
        doc = Document(doc_text, len(doc_text))
        event = CompleteEvent()
        completions = [
            completion.text
            for completion in list(completer.get_completions(doc, event))
        ]
        self.assertEqual(sorted(completions), ["hello", "hey"])

    def test_prompt_message(self):
        input_prompt = InputPrompt(message="Enter your name", style={}, symbol="[?]")
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "[?]"),
                ("class:question", " Enter your name"),
                ("class:instruction", " "),
            ],
        )
        input_prompt.status["answered"] = True
        input_prompt.status["result"] = "haha"
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "[?]"),
                ("class:question", " Enter your name"),
                ("class:answer", " haha"),
            ],
        )

        input_prompt = InputPrompt(
            message="Enter your name",
            style={},
            default="",
            symbol="[?]",
            editing_mode="emacs",
            multiline=True,
            completer={"hello": None, "hey": None, "what": None},
        )
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "[?]"),
                ("class:question", " Enter your name"),
                ("class:instruction", " ESC + Enter to finish input"),
                ("class:symbol", "\n%s " % INQUIRERPY_POINTER_SEQUENCE),
            ],
        )
        input_prompt.status["answered"] = True
        input_prompt.status["result"] = "haha\n123"
        message = input_prompt._get_prompt_message()
        self.assertEqual(
            message,
            [
                ("class:symbol", "[?]"),
                ("class:question", " Enter your name"),
                ("class:answer", " haha...[3 chars]"),
            ],
        )

    @patch("InquirerPy.prompts.input.Validator.from_callable")
    @patch("InquirerPy.prompts.input.NestedCompleter.from_nested_dict")
    @patch("InquirerPy.prompts.input.SimpleLexer")
    @patch("InquirerPy.prompts.input.InputPrompt._get_prompt_message")
    @patch("InquirerPy.base.Style.from_dict")
    @patch("InquirerPy.base.KeyBindings")
    @patch("InquirerPy.prompts.input.PromptSession")
    def test_callable_called(
        self,
        MockedSession,
        MockedKeyBindings,
        MockedStyle,
        mocked_message,
        MockedLexer,
        mocked_completer,
        mocked_validator,
    ):
        completer = mocked_completer()
        validator = mocked_validator()
        kb = MockedKeyBindings()
        style = MockedStyle()
        lexer = MockedLexer()
        InputPrompt(
            message="Enter your name",
            style={},
            default="",
            symbol="[?]",
            editing_mode="emacs",
            multiline=True,
            completer={"hello": None, "hey": None, "what": None},
        )
        MockedSession.assert_called_once_with(
            message=mocked_message,
            key_bindings=kb,
            style=style,
            completer=completer,
            validator=validator,
            validate_while_typing=False,
            input=None,
            output=None,
            editing_mode=EditingMode.EMACS,
            lexer=lexer,
            is_password=False,
            multiline=True,
        )
        mocked_validator.assert_has_calls(
            [call(ANY, "Invalid input", move_cursor_to_end=True)]
        )
        mocked_completer.assert_has_calls(
            [call({"hello": None, "hey": None, "what": None})]
        )
        MockedStyle.assert_has_calls([call({})])
        MockedLexer.assert_has_calls([call("class:input")])