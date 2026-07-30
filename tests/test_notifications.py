import pytest
from unittest.mock import patch, MagicMock
from automation.send_notifications import send_telegram_message

@patch("requests.post")
def test_send_telegram_message(mock_post):
    """Testa l'invio del messaggio Telegram (mockato)."""
    # Mock variabili d'ambiente
    with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test_token", "TELEGRAM_CHAT_ID": "test_id"}):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        send_telegram_message("Test message")

        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["chat_id"] == "test_id"
        assert "Test message" in kwargs["json"]["text"]
