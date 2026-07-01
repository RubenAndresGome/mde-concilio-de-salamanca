import os
import sys
import shutil
import subprocess
import urllib.parse
from typing import Optional

class WebsiteDownloaderWrapper:
    """
    Wrapper para Website-downloader.
    Ejecuta el comando wget similar al proyecto original en Node.js,
    o utiliza un fallback puro de Python si no se encuentran las herramientas.
    """

    def __init__(self, output_base_dir: Optional[str] = None):
        self.output_base_dir = output_base_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "temp_downloads"
        )
        os.makedirs(self.output_base_dir, exist_ok=True)

    def is_wget_available(self) -> bool:
        return shutil.which("wget") is not None

    def is_node_available(self) -> bool:
        return shutil.which("node") is not None

    def _download_via_wget(self, url: str) -> str:
        """Equivalente exacto del core de AhmadIbrahiim/Website-downloader"""
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        dest_dir = os.path.join(self.output_base_dir, domain)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Wget flags used by AhmadIbrahiim/Website-downloader:
        # -m (mirror), -k (convert-links), -E (adjust-extension), -p (page-requisites), -np (no-parent)
        cmd = ["wget", "-mkEpnp", "--no-if-modified-since", "-P", dest_dir, url]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return dest_dir
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error al ejecutar wget: {e.stderr.decode('utf-8', errors='ignore')}")

    def _download_via_python_fallback(self, url: str) -> str:
        """Fallback si wget no está en el PATH de Windows."""
        import urllib.request
        from html.parser import HTMLParser
        
        class LinkExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stylesheets = []

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                if tag == "link" and attrs_dict.get("rel") == "stylesheet":
                    href = attrs_dict.get("href")
                    if href:
                        self.stylesheets.append(href)

        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc or "downloaded_site"
        dest_dir = os.path.join(self.output_base_dir, domain)
        os.makedirs(dest_dir, exist_ok=True)
        
        index_path = os.path.join(dest_dir, "index.html")
        
        # Descarga la página principal
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                html_content = response.read()
                
            with open(index_path, "wb") as f:
                f.write(html_content)
                
            # Intenta descargar assets básicos
            parser = LinkExtractor()
            try:
                parser.feed(html_content.decode('utf-8', errors='ignore'))
            except Exception:
                pass
            
            # Descargar hojas de estilo CSS
            for href in parser.stylesheets:
                asset_url = urllib.parse.urljoin(url, href)
                asset_name = os.path.basename(urllib.parse.urlparse(asset_url).path) or "style.css"
                asset_path = os.path.join(dest_dir, asset_name)
                try:
                    req_asset = urllib.request.Request(asset_url, headers=headers)
                    with urllib.request.urlopen(req_asset, timeout=5) as res:
                        with open(asset_path, "wb") as f:
                            f.write(res.read())
                except Exception:
                    pass # Silenciar fallos en descargas de assets secundarios
                        
            return dest_dir
        except Exception as e:
            raise RuntimeError(f"Fallback de Python falló al descargar {url}: {str(e)}")

    def download(self, url: str) -> str:
        """Intenta descargar usando wget y cae a fallback en Python si no está disponible."""
        if self.is_wget_available():
            try:
                return self._download_via_wget(url)
            except Exception as e:
                print(f"[Warn] Wget falló, intentando fallback de Python... Detalle: {e}", file=sys.stderr)
                return self._download_via_python_fallback(url)
        else:
            return self._download_via_python_fallback(url)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python website_downloader_wrapper.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    downloader = WebsiteDownloaderWrapper()
    print(f"Descargando {url}...")
    try:
        path = downloader.download(url)
        print(f"Descarga completa en: {path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
