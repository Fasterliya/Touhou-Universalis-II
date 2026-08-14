import urllib.request, re, zipfile, sys, time, io
from urllib.parse import urljoin

LOG = io.StringIO()
def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + '\n')

base = r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II\tools'
MIRRORS = [
    'https://mirrors.aliyun.com/pypi/simple/pyyaml/',
    'https://pypi.tuna.tsinghua.edu.cn/simple/pyyaml/',
    'https://mirrors.cloud.tencent.com/pypi/simple/pyyaml/',
    'https://pypi.org/simple/pyyaml/',
]
TARGET = 'cp314-cp314-win_amd64.whl'

def fetch(url, timeout=60, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'th-validator/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            log(f'  retry {i+1} {url[:90]}: {e}')
            time.sleep(2)
    raise last

whl_url = None
for mirror in MIRRORS:
    try:
        log('trying', mirror)
        html = fetch(mirror, timeout=60, tries=2).decode('utf-8', 'replace')
        log('  got', len(html), 'bytes; has cp314:', 'cp314' in html)
        m = re.search(r'href="([^"]*' + re.escape(TARGET) + r'[^"]*)"', html)
        if m:
            href = m.group(1).split('#')[0]
            whl_url = urljoin(mirror, href)
            log('  wheel url:', whl_url)
            break
        else:
            log('  cp314 wheel not found in index')
    except Exception as e:
        log(f'mirror failed {mirror}: {e}')

if not whl_url:
    log('NO WHEEL URL FOUND')
    with open(base + r'\fetch_log.txt', 'w', encoding='utf-8') as f:
        f.write(LOG.getvalue())
    sys.exit(1)

whl_path = base + r'\pylibs\pyyaml.whl'
data = fetch(whl_url, timeout=180, tries=6)
with open(whl_path, 'wb') as f:
    f.write(data)
log('downloaded', len(data), 'bytes')

with zipfile.ZipFile(whl_path) as z:
    z.extractall(base + r'\pylibs')
log('extracted')

sys.path.insert(0, base + r'\pylibs')
import yaml
log('PyYAML OK', yaml.__version__)
with open(base + r'\fetch_log.txt', 'w', encoding='utf-8') as f:
    f.write(LOG.getvalue())
print('DONE')
