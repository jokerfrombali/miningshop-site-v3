# -*- coding: utf-8 -*-
"""301-редиректы со старого miningshop.ru (Битрикс, 2017 — январь 2026) на новую структуру.

Список старых адресов — data/legacy_urls.txt, собран из архива miningshop-old (товары, разделы, страницы).
После переезда в январе 2026 эти адреса отдавали 404 и теряли накопленный с 2017 года вес.
Правило: если адрес есть на новом сайте — он и остаётся; иначе ведём на ближайший живой раздел.
Адреса, которым некуда вести, оставляем 404 — редирект «всего на главную» поисковики считают ошибкой.
"""
import os, re

HERE = os.path.dirname(__file__)
VK = '/catalog/videokarty/'
KP = '/catalog/komplektuyushchie/'

GPU_WORDS = [  # (что ищем в адресе, куда ведём)
    (r'3090', VK + 'rtx-3090/'), (r'4090', VK + 'rtx-4090/'), (r'5090', VK + 'rtx-5090/'),
    (r'v100', VK + 'tesla-v100/'), (r'p40\b|_p40', VK + 'tesla-p40/'), (r'p100', VK + 'tesla-p100/'),
    (r'a100', VK + 'a100/'), (r'h100', VK + 'h100/'), (r'a6000', VK + 'rtx-a6000/'), (r'a4000|a5000', VK + 'rtx-a4000-a5000/'),
    (r'tesla', VK + 'nvidia-tesla/'), (r'p102|p104|p106|cmp', '/blog/cmp-170hx-90hx/'),
]

ROOT_LANDINGS = {
    'bloki_pitaniya_dlya_majninga': KP + 'bloki_pitaniya/', 'karkas_dlja_majning_fermy': KP + 'korpusa_i_karkasy/',
    'materinskaja_plata_dlja_majninga': KP + 'materinskie_platy/', 'processor_dlya_majninga': KP + 'materinskie_platy/',
    'operativnaja_pamjat_dlja_majninga': KP + 'materinskie_platy/', 'rajzer_dlya_videokarty': KP + 'rayzery/',
    'kuler_dlya_majninga': KP + 'okhlazhdenie/', 'komplektuyushchie_used': KP, 'zhestkij_disk_dlja_majninga': KP,
    'm2_perehodniki': KP, 'maining_fermy_used': '/catalog/mayning_fermy/', 'asic_maineri': '/catalog/asic_maynery/',
    'about': '/company/about/', 'info': '/company/delivery/', 'help': '/company/delivery/', 'projects': '/services/',
    'partner': '/contacts/', 'clients': '/contacts/', 'contacts': '/contacts/', 'company': '/company/about/',
    'knowledge': '/blog/', 'blog': '/blog/', 'services': '/services/',
}


# Близкие модели: старой карточки на новом сайте нет, но есть прямой преемник той же линейки
ASIC_SUCCESSOR = {'s19': 's19-pro', 'l3': 'l7', 'm30s': 'm30s-plus', 'm31s-plus': 'm30s-plus'}


def asic_model(slug):
    """'bitmain_antminer_s19_pro' и 'antminer-s19-pro-110th' -> 's19-pro'; None, если модель не распознана."""
    s = slug.lower().replace('_', '-').strip('-')
    s = re.sub(r'^(bitmain-)?antminer-|^whatsminer-', '', s)
    s = re.sub(r'-\d+(\.\d+)?(th|gh|mh|ksol)$', '', s)
    s = s.replace('plus-plus', 'pp')
    if not re.fullmatch(r'[a-z]{1,2}\d{1,2}[a-z]?(-(pro|xp|plus|pp|hyd|hydro|k-pro|j-pro))*', s):
        return None
    s = s.replace('hydro', 'hyd')
    return ASIC_SUCCESSOR.get(s, s)


# Первый сайт на OpenCart (2017–2018): разделы в корне адреса. Ведём только туда, где есть та же вещь;
# клавиатуры, мыши, роутеры и прочее, чего на новом сайте нет, остаются 404.
OPENCART = {
    'fermy_dlja_majninga_kriptovaljuty': '/catalog/mayning_fermy/', 'sborka_i_nastrojka_majning_ferm': '/services/mining-pod-kljuch/',
    'franshiza_majning': '/services/mining-pod-kljuch/', 'investicii_majning_promyshlennaya_ferma': '/services/mining-pod-kljuch/',
    'videokarty_dlya_majninga': VK, 'nvidia': VK + 'videokarty_nvidia/', 'palit': VK + 'videokarty_nvidia/',
    'gigabyte': VK, 'colorful': VK, 'evga': VK, 'powercolor': VK + 'radeon-ai-pro/', 'sapphire': VK + 'radeon-ai-pro/',
    'amd': VK + 'radeon-ai-pro/', 'used_asics': '/catalog/asic_maynery/', 'bitmain': '/catalog/asic_maynery/bitmain/',
    's9i_s9j': '/catalog/asic_maynery/bitmain/', 'asicminer': '/catalog/asic_maynery/', 'bitfury': '/catalog/asic_maynery/',
    'ebang': '/catalog/asic_maynery/', 'canaan': '/catalog/asic_maynery/', 'pangolin': '/catalog/asic_maynery/',
    'dayun': '/catalog/asic_maynery/', 'asrock': KP + 'materinskie_platy/', 'esonics': KP + 'materinskie_platy/',
    'intel': KP + 'materinskie_platy/', 'corsair': KP + 'bloki_pitaniya/', 'chieftec': KP + 'bloki_pitaniya/',
    'thermaltake': KP + 'bloki_pitaniya/', 'cougar': KP + 'bloki_pitaniya/', 'aerocool': KP + 'bloki_pitaniya/',
    'provoda_dlja_majning_fermy': KP, 'vatchdogi': KP, 'emulyator-monitora': KP, 'katalog': '/catalog/',
    'o_nas': '/company/about/', 'terms-of-use': '/terms/', 'sale': '/catalog/', 'do': '/services/remont-oborudovaniya/',
}


def target(path, known):
    """Куда вести старый адрес. None — оставить 404, 'GONE' — 410."""
    if path in known:
        return None
    low = path.lower()
    parts = [x for x in low.split('/') if x]
    if not parts:
        return None
    if parts[0] == 'forum':
        return 'GONE'
    if parts[0] == 'seo' and 's21-xp-hyd' in low:
        return '/catalog/asic_maynery/bitmain/antminer-s21-xp-hydro-473th/'
    if parts[0] in ('news', 'knowledge'):
        return '/blog/'
    if parts[0] == 'services':
        return {'remont-asikov': '/services/remont-oborudovaniya/', 'ustanovka-proshivki-razgon': '/services/remont-oborudovaniya/',
                'meeting': '/contacts/'}.get(parts[1] if len(parts) > 1 else '', '/services/')
    if parts[0] == 'about' and len(parts) > 1:
        return {'delivery': '/company/delivery/', 'guaranty': '/company/guarantee/', 'contacts': '/contacts/'}.get(parts[1], '/company/about/')
    if parts[0] in OPENCART:
        dst = OPENCART[parts[0]]
        if parts[0] in ('fermy_dlja_majninga_kriptovaljuty', 'videokarty_dlya_majninga') and len(parts) > 1:
            if '3090' in low:
                return '/catalog/mayning_fermy/na-rtx-3090/' if parts[0].startswith('fermy') else VK + 'rtx-3090/'
            if parts[0].startswith('videokarty'):
                for pat, d in GPU_WORDS:
                    if re.search(pat, low):
                        return d
                return VK + 'bu/'
        return dst
    if parts[0] != 'catalog':
        return ROOT_LANDINGS.get(parts[0])
    sec = parts[1] if len(parts) > 1 else ''
    if sec == 'videokarty':
        if len(parts) == 2:
            return None
        if 'videokarty_geforce_rtx_30' in low and len(parts) == 4:
            return VK + 'rtx-3090/'      # раздел RTX 30: 19 тыс. входов; из серии под ИИ востребована только 3090 24 ГБ
        for pat, dst in GPU_WORDS:
            if re.search(pat, low):
                return dst
        if 'videokarty_amd' in low or 'radeon' in low or '_rx_' in low:
            return VK + 'radeon-ai-pro/' if len(parts) <= 3 else VK + 'bu/'
        return VK if len(parts) <= 4 and not re.search(r'\d', parts[-1]) else VK + 'bu/'
    if sec in ('fermy_dlya_mayninga', 'mayning_fermy'):
        if 'tushka' in low:
            return '/catalog/sborki-dlya-ii/platformy/'
        if '3090' in low:
            return '/catalog/mayning_fermy/na-rtx-3090/'     # 19 тыс. входов в 2021–2022 — на ферму той же карты
        if re.search(r'3080|3070|3060|_nvidia|p102|p104', low) and 'videokarty_dlya_mayninga' not in low:
            return '/catalog/mayning_fermy/mayning_fermy_na_nvidia/'
        if 'videokarty_dlya_mayninga' in low:
            return '/blog/cmp-170hx-90hx/'
        return '/catalog/mayning_fermy/'
    if sec in ('komplektuyushchie', 'dop_tovary_i_uslugi', 'dopolnitelnye_tovary', 'zhestkie_diski_dlya_mayninga'):
        for pat, dst in ((r'rayzer|rajzer|riser', KP + 'rayzery/'), (r'immersion', KP + 'zhidkostnoe-okhlazhdenie/'),
                         (r'blok_pitaniya|bloki_pitaniya|psu|_bp_', KP + 'bloki_pitaniya/'),
                         (r'materinsk|protsessor|operativn|_cpu|celeron|b250|h110|h310', KP + 'materinskie_platy/'),
                         (r'korpus|karkas|korob', KP + 'korpusa_i_karkasy/'), (r'okhlazhd|kuler|ventil', KP + 'okhlazhdenie/'),
                         (r'shumobox|shumoboks', KP + 'shumoboksy/'), (r'konteyner', KP + 'konteynery/')):
            if re.search(pat, low):
                return dst
        return KP
    if sec == 'asic_maynery':
        model = asic_model(parts[-1]) if len(parts) >= 4 else None
        if model:
            for k in sorted(known):    # та же модель есть на новом сайте под новым адресом — ведём на карточку, а не на бренд
                if k.startswith('/catalog/asic_maynery/') and k.count('/') == 5 and asic_model(k.split('/')[-2]) == model:
                    return k
        for brand in ('bitmain', 'whatsminer', 'ipollo', 'jasminer'):
            if brand in low and '/catalog/asic_maynery/%s/' % brand in known:
                return '/catalog/asic_maynery/%s/' % brand
        return '/catalog/asic_maynery/'
    if sec == 'remont_asikov':
        return '/services/remont-oborudovaniya/'
    if sec in ('zakazy', ''):
        return '/catalog/'
    return '/catalog/'


def build(known):
    """Возвращает [(старый адрес, новый адрес или 'GONE')] для всех старых адресов, которые не совпадают с новыми."""
    old = [x.strip() for x in open(os.path.join(HERE, 'data', 'legacy_urls.txt'), encoding='utf-8') if x.strip()]
    # адреса входа из Метрики 2021–2025 (data/legacy_weight.tsv): часть самых сильных старых адресов в архиве страниц
    # не сохранилась, и без этого они отдавали бы 404 — например, /catalog/fermy_dlya_mayninga/ с 86 тыс. входов
    oc = os.path.join(HERE, 'data', 'legacy_opencart.txt')   # 566 адресов первого сайта из архива
    if os.path.exists(oc):
        old += [x.strip() for x in open(oc, encoding='utf-8') if x.strip()]
    wf = os.path.join(HERE, 'data', 'legacy_weight.tsv')
    if os.path.exists(wf):
        old += [l.split('\t')[3] for l in open(wf, encoding='utf-8').read().splitlines()[1:] if l.count('\t') >= 4]
    old += ['/knowledge/', '/forum/', '/news/', '/seo/antminer-s21-xp-hyd/'] + [
        '/knowledge/%s/' % r for r in ('basics', 'hardware', 'maintenance', 'security', 'setup', 'software')]
    out = []
    for path in sorted(set(old)):
        dst = target(path, known)
        if dst and dst != path:
            assert dst == 'GONE' or dst in known, (path, dst)
            out.append((path, dst))
    return out


def apache_rx(path):
    """Регулярное выражение для RedirectMatch: Apache сравнивает с раскодированным адресом (%20 -> пробел, %D0%B0 -> «а»),
    а пробел в строке .htaccess разрывает директиву и даёт ошибку 500 на весь сайт — поэтому пробел пишем как \\s."""
    from urllib.parse import unquote
    return re.escape(unquote(path).rstrip('/')).replace('\\ ', '\\s')


def htaccess(rules, prod):
    host = prod.split('//', 1)[1]
    hrx = re.escape(host)
    lines = ['# Сгенерировано src/redirects.py — правьте там, а не здесь.', 'Options -Indexes', 'ErrorDocument 404 /404.html', '',
             '# Один адрес сайта: https://%s без www. Всё остальное — 301 сюда же, с тем же путём.' % host,
             '# Timeweb принимает https на прокси, поэтому протокол смотрим и в %{HTTPS}, и в X-Forwarded-Proto.',
             '<IfModule mod_rewrite.c>', 'RewriteEngine On',
             'RewriteCond %{HTTP_HOST} !^' + hrx + '$ [NC]',
             'RewriteRule ^ https://' + host + '%{REQUEST_URI} [L,R=301,NE]',
             'RewriteCond %{HTTPS} !=on',
             'RewriteCond %{HTTP:X-Forwarded-Proto} !=https',
             'RewriteRule ^ https://' + host + '%{REQUEST_URI} [L,R=301,NE]',
             '</IfModule>', '']
    seen = set()
    for old, new in rules:
        rx = apache_rx(old)
        if rx in seen:          # «/a b/» и «/a%20b/» — один и тот же адрес для Apache
            continue
        seen.add(rx)
        if new == 'GONE':
            lines.append('RedirectMatch 410 ^%s(/.*)?$' % rx)
        else:
            lines.append('RedirectMatch 301 ^%s/?$ %s%s' % (rx, prod, new))
    for l in lines:
        assert not l.startswith('RedirectMatch') or len(l.split()) == (3 if ' 410 ' in l else 4), l
    return '\n'.join(lines) + '\n'
