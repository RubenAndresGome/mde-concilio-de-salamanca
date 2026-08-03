from unittest.mock import MagicMock, patch
from concilio_salamanca.tools.website_downloader_wrapper import WebsiteDownloaderWrapper

def test_downloader_wget_available():
    with patch("shutil.which", return_value="/usr/bin/wget"):
        downloader = WebsiteDownloaderWrapper()
        assert downloader.is_wget_available() is True

def test_downloader_wget_unavailable():
    with patch("shutil.which", return_value=None):
        downloader = WebsiteDownloaderWrapper()
        assert downloader.is_wget_available() is False

@patch("subprocess.run")
def test_download_via_wget(mock_run):
    downloader = WebsiteDownloaderWrapper()
    with patch.object(downloader, "is_wget_available", return_value=True):
        with patch("os.makedirs"):
            downloader.download("http://example.com")
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "wget" in args
            assert "http://example.com" in args

@patch("urllib.request.urlopen")
def test_download_via_python_fallback(mock_urlopen):
    # Mocking urlopen to return mock response for index.html and CSS
    mock_response = MagicMock()
    mock_response.read.return_value = b"<html><head><link rel='stylesheet' href='styles.css'></head><body>Hello</body></html>"
    mock_urlopen.return_value.__enter__.return_value = mock_response

    downloader = WebsiteDownloaderWrapper()
    with patch.object(downloader, "is_wget_available", return_value=False):
        with patch("os.makedirs"):
            with patch("builtins.open", create=True) as mock_open:
                path = downloader.download("http://example.com")
                assert "example.com" in path
                # Should attempt to open index.html and write to it
                mock_open.assert_called()
