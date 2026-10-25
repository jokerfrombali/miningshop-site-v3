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
    if parts[0] == 'services':
        return {'remont-asikov': '/services/remont-oborudovaniya/', 'ustanovka-proshivki-razgon': '/services/remont-oborudovaniya/',
                'meeting': '/contacts/'}.get(parts[1] if len(parts) > 1 else '', '/services/')
    if parts[0] == 'about' and len(parts) > 1:
        return {'delivery': '/company/delivery/', 'guaranty': '/company/guarantee/', 'contacts': '/contacts/'}.get(parts[1], '/company/about/')
    if parts[0] != 'catalog':
        return ROOT_LANDINGS.get(parts[0])
    sec = parts[1] if len(parts) > 1 else ''
    if sec == 'videokarty':
        if len(parts) == 2:
            return None
        for pat, dst in GPU_WORDS:
            if re.search(pat, low):
                return dst
        if 'videokarty_amd' in low or 'radeon' in low or '_rx_' in low:
            return VK + 'radeon-ai-pro/' if len(parts) <= 3 else VK + 'bu/'
        return VK if len(parts) <= 4 and not re.search(r'\d', parts[-1]) else VK + 'bu/'
    if sec in ('fermy_dlya_mayninga', 'mayning_fermy'):
        if 'tushka' in low:
            return '/catalog/sborki-dlya-ii/platformy/'
        if re.search(r'3090|3080|3070', low):
            return '/catalog/sborki-dlya-ii/4x-rtx-3090/'
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
    old += ['/knowledge/', '/forum/']
    out = []
    for path in sorted(set(old)):
        dst = target(path, known)
        if dst and dst != path:
            assert dst == 'GONE' or dst in known, (path, dst)
            out.append((path, dst))
    return out


def htaccess(rules, prod):
    lines = ['# Сгенерировано src/redirects.py — правьте там, а не здесь.', 'Options -Indexes', 'ErrorDocument 404 /404.html', '']
    for old, new in rules:
        rx = '^' + re.escape(old.rstrip('/')) + '/?$'
        if new == 'GONE':
            lines.append('RedirectMatch 410 ^%s(/.*)?$' % re.escape(old.rstrip('/')))
        else:
            lines.append('RedirectMatch 301 %s %s%s' % (rx, prod, new))
    return '\n'.join(lines) + '\n'
