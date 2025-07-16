import time
from typing import Optional
from tenacity import retry, stop_after_delay, wait_fixed


def is_loader_hide(
        page,
        css_selector: str = '.ngx-overlay',
        timeout: int = 30,
        poll_interval: float = 0.2
) -> bool:
    @retry(stop=stop_after_delay(timeout), wait=wait_fixed(poll_interval))
    def check_loader() -> Optional[bool]:
        try:
            loader = page.ele(f'css:{css_selector}', timeout=0.5, show_errmsg=False)
            if loader:
                class_attr = loader.attr('class', '')
                if 'ngx-overlay' in class_attr.split():
                    raise ValueError("Loader still visible")
            return True
        except Exception:
            return None

    start_time = time.time()
    result = check_loader()

    if result is True:
        print(f"Loader disappear for ({time.time() - start_time:.1f})")
        return True

    page.screenshot('loader_timeout.png')
    raise TimeoutError(f"Loader not disappear for({timeout})")
