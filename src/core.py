# -*- coding: utf-8 -*-
"""Каркас сайта: контакты, блоки разметки, шаблон страницы, SEO-метаданные.

Сайт собирается в статический HTML. BASE — префикс адресов: на GitHub Pages сайт живёт
в подпапке /miningshop-site/, на боевом домене префикс пустой. Все внутренние ссылки
строятся через u(), поэтому переезд — это смена одной переменной.
"""
import html, json, os, re

BASE = os.environ.get('MS_BASE', '/miningshop-site-v3')
PROD = 'https://miningshop.ru'            # canonical всегда указывает на будущий боевой адрес
TEMPORARY = os.environ.get('MS_TEMP', '1') == '1'
METRIKA = 45472341   # счётчик miningshop.ru с 2017 года — не менять, иначе потеряется история

METRIKA_JS = ('<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();'
              'for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}'
              'k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})'
              '(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");'
              'ym(%d,"init",{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true});</script>'
              '<noscript><div><img src="https://mc.yandex.ru/watch/%d" style="position:absolute;left:-9999px" alt=""></div></noscript>'
              % (METRIKA, METRIKA))

C = {
    'brand': 'MiningShop',
    'phone': '+7 (999) 499-96-96', 'phone_href': 'tel:+79994999696', 'phone_note': '',
    'email': 'info@miningshop.ru',
    'tg': 'https://t.me/miningshop', 'tg_name': '@miningshop',
    'youtube': 'https://www.youtube.com/channel/UCZuNz7CLAENZIeyAooKW0oQ',   # канал со старого сайта
    'tg_channel': 'https://t.me/miningshop_official',
    'address': 'г. Москва, шоссе Энтузиастов, 56, стр. 20',
    'hours': 'Пн–Пт 10:00–19:00',
    'hours_short': 'Пн–Пт 10–19',
    'since': 2017,
}


def u(path):
    """Внутренний адрес с учётом префикса."""
    if path.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
        return path
    return BASE + path


def esc(s):
    return html.escape(s, quote=True)


# ------------------------------------------------------------------ иконки
ICONS = {
    'phone': '<path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/>',
    'mail': '<path d="M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm8 7.2L4.6 7.3v9.7h14.8V7.3z"/>',
    'tg': '<path d="M21.5 4.3 2.9 11.5c-1.3.5-1.2 1.2-.2 1.5l4.8 1.5 1.8 5.6c.2.6.1.9.8.9.5 0 .7-.2 1-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8l3.1-14.7c.3-1.3-.5-1.9-1.5-1z"/>',
    'chip': '<path d="M9 3v2H7a2 2 0 0 0-2 2v2H3v2h2v2H3v2h2v2a2 2 0 0 0 2 2h2v2h2v-2h2v2h2v-2h2a2 2 0 0 0 2-2v-2h2v-2h-2v-2h2V9h-2V7a2 2 0 0 0-2-2h-2V3h-2v2h-2V3zm-1 5h8v8H8z"/>',
    'bolt': '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
    'shield': '<path d="M12 2 4 5v6c0 5 3.4 9.7 8 11 4.6-1.3 8-6 8-11V5z"/>',
    'truck': '<path d="M3 5h11v9h2.5l2.5-3.5H21V17h-1.5a2.5 2.5 0 0 1-5 0h-5a2.5 2.5 0 0 1-5 0H3z"/>',
    'wrench': '<path d="M22 7.5a5.5 5.5 0 0 1-7.4 5.2L7.4 20a2 2 0 1 1-2.8-2.8l7.2-7.2A5.5 5.5 0 0 1 18.5 2l-3 3 .9 2.6 2.6.9z"/>',
    'server': '<path d="M4 3h16a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zm0 11h16a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-5a1 1 0 0 1 1-1zm2-8v1h2V6zm0 11v1h2v-1z"/>',
    'calc': '<path d="M6 2h12a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm1 3v4h10V5zm0 7v2h2v-2zm4 0v2h2v-2zm4 0v6h2v-6zm-8 4v2h2v-2zm4 0v2h2v-2z"/>',
    'doc': '<path d="M6 2h8l6 6v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm7 1.5V9h5.5zM8 13v2h8v-2zm0 4v2h8v-2z"/>',
    'fan': '<path d="M12 11a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm.6-9C17 2 17.5 7 14 9.5c3.5-1 7.3 1.9 6 6-1.4 4.3-6.4 2.4-7.4-1.4.1 3.6-3.3 6.7-7 4.6-3.9-2.2-.9-6.8 2.7-7.4C4.8 9.9 3.5 5 7.3 3.2c1.8-.9 3.7-1.2 5.3-1.2z"/>',
    'user': '<path d="M12 12a5 5 0 1 0 0-10 5 5 0 0 0 0 10zm0 2c-5 0-9 2.5-9 5.5V22h18v-2.5C21 16.5 17 14 12 14z"/>',
    'box': '<path d="M12 2 3 6.5v11L12 22l9-4.5v-11zm0 2.2 6.5 3.3L12 10.8 5.5 7.5zM5 9.2l6 3v7.4l-6-3zm14 0v7.4l-6 3v-7.4z"/>',
    'chart': '<path d="M4 20V10h3v10zm6 0V4h3v16zm6 0v-7h3v7zM3 21h18v1H3z"/>',
    'burger': '<path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/>',
    'snow': '<path d="M11 2h2v4.3l2.3-2.3 1.4 1.4L13 9.1V11h1.9l3.7-3.7 1.4 1.4L17.7 11H22v2h-4.3l2.3 2.3-1.4 1.4L14.9 13H13v1.9l3.7 3.7-1.4 1.4-2.3-2.3V22h-2v-4.3L8.7 20l-1.4-1.4L11 14.9V13H9.1l-3.7 3.7L4 15.3 6.3 13H2v-2h4.3L4 8.7l1.4-1.4L9.1 11H11V9.1L7.3 5.4 8.7 4 11 6.3z"/>',
    'yt': '<path d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8c1.6.4 7.8.4 7.8.4s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8zM10 15V9l5.2 3z"/>',
    'search': '<path d="M10.5 3a7.5 7.5 0 0 1 6 12l4.8 4.8-1.5 1.5-4.8-4.8A7.5 7.5 0 1 1 10.5 3zm0 2a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11z"/>',
}


def icon(name, cls=''):
    return '<svg class="%s" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">%s</svg>' % (cls, ICONS[name])


# ------------------------------------------------------------------ блоки текста
def h2(text, anchor=''):
    return '<h2%s>%s</h2>' % (' id="%s"' % anchor if anchor else '', text)


def h3(text):
    return '<h3>%s</h3>' % text


def p(*parts):
    return ''.join('<p>%s</p>' % x for x in parts)


def ul(items):
    return '<ul>%s</ul>' % ''.join('<li>%s</li>' % i for i in items)


def ol(items):
    return '<ol>%s</ol>' % ''.join('<li>%s</li>' % i for i in items)


def note(title, text):
    return '<div class="note"><b>%s</b>%s</div>' % (title, text)


def table(headers, rows):
    th = ''.join('<th>%s</th>' % h for h in headers)
    tr = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)
    return '<div class="tbl-wrap"><table class="tbl"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, tr)


def ptable(headers, rows):
    """Таблица внутри текстовой колонки (без горизонтальной прокрутки на ПК)."""
    th = ''.join('<th>%s</th>' % h for h in headers)
    tr = ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)
    return '<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (th, tr)


def a(href, text):
    return '<a href="%s">%s</a>' % (u(href), text)


def faq_html(items):
    return '<div class="faq">%s</div>' % ''.join(
        '<details><summary>%s</summary><div>%s</div></details>' % (q, ans) for q, ans in items)


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": re.sub(r'<[^>]+>', '', q),
         "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', ans)}} for q, ans in items]}


def cards(items, cols=3, link=False):
    """items: (icon|None, заголовок, текст[, href])"""
    out = []
    for it in items:
        ic, title, text = it[0], it[1], it[2]
        href = it[3] if len(it) > 3 else None
        inner = ('<div class="ico">%s</div>' % icon(ic) if ic else '') + '<h3>%s</h3><p>%s</p>' % (title, text)
        if href:
            out.append('<a class="card card-link" href="%s">%s<span class="more">Подробнее →</span></a>' % (u(href), inner))
        else:
            out.append('<div class="card">%s</div>' % inner)
    return '<div class="grid g%d">%s</div>' % (cols, ''.join(out))


def steps(items):
    return '<ol class="steps">%s</ol>' % ''.join('<li><b>%s</b>%s</li>' % (t, d) for t, d in items)


def cta_box(title, text, href='/contacts/', label='Обсудить задачу'):
    return ('<div class="cta-box"><h3>%s</h3><p>%s</p><a class="btn btn-accent" href="%s">%s</a>'
            '<p style="margin:14px 0 0;font-size:14px">или позвоните: <a href="%s" style="color:#ff5c82;text-decoration:none">%s</a></p></div>'
            % (title, text, u(href), label, C['phone_href'], C['phone']))


def section(inner, cls='', title='', sub='', center=False, anchor=''):
    head = ''
    if title:
        head = '<h2>%s</h2>' % title + ('<p class="sub">%s</p>' % sub if sub else '')
    return '<section class="sec %s"%s><div class="wrap%s">%s%s</div></section>' % (
        cls, ' id="%s"' % anchor if anchor else '', ' center' if center else '', head, inner)


def toc(items):
    return '<nav class="toc"><b>Содержание</b>%s</nav>' % ''.join(
        '<a href="#%s">%s</a>' % (anc, t) for t, anc in items)


def trust():
    items = [('shield', 'Тест 24 часа', 'каждую сборку гоняем под нагрузкой и даём отчёт'),
             ('wrench', 'Гарантия на сборку', 'и консультации после покупки'),
             ('truck', 'Доставка по России', 'транспортными компаниями или самовывоз в Москве'),
             ('calc', 'Выкуп и трейд-ин', 'старые карты — в зачёт новой покупки')]
    return ('<div class="trust"><div class="wrap">%s</div></div>'
            % ''.join('<div><span class="ico">%s</span><b>%s</b><small>%s</small></div>' % (icon(i), t, d) for i, t, d in items))


# ------------------------------------------------------------------ живые фото (свои снимки старого сайта, src/static/img/photos)
def photo(name, alt, cap='', eager=False):
    src = u('/assets/img/photos/%s.webp' % name)
    sm = u('/assets/img/photos/%s-sm.webp' % name)
    return ('<figure class="photo"><img src="%s" srcset="%s 700w, %s 1400w" sizes="(max-width:760px) 100vw, 50vw" alt="%s"%s>%s</figure>'
            % (src, sm, src, esc(alt), '' if eager else ' loading="lazy"', '<figcaption>%s</figcaption>' % cap if cap else ''))


def gallery(items, cols=3):
    """items: (имя файла, alt, подпись)"""
    return '<div class="gallery g%d">%s</div>' % (cols, ''.join(photo(*it) for it in items))


# ------------------------------------------------------------------ шаблон
NAV = [
    ('Видеокарты', '/catalog/videokarty/'),
    ('Серверы для ИИ', '/catalog/servery-dlya-ii/'),
    ('GPU-фермы', '/catalog/mayning_fermy/'),
    ('Сборки', '/catalog/sborki-dlya-ii/'),
    ('Комплектующие', '/catalog/komplektuyushchie/'),
    ('Выкуп', '/services/vykup-videokart/'),
    ('Асики', '/catalog/asic_maynery/'),
    ('Статьи', '/blog/'),
    ('Контакты', '/contacts/'),
]


# мега-меню «Каталог»: как на старом сайте на Битриксе — все разделы сразу, с подразделами
MEGA = [
    ('Серверы для ИИ', '/catalog/servery-dlya-ii/', [('Сервер для LLM', '/catalog/servery-dlya-ii/dlya-llm/'),
        ('Для обучения нейросетей', '/catalog/servery-dlya-ii/dlya-obucheniya/'), ('На 8 GPU', '/catalog/servery-dlya-ii/na-8-gpu/'),
        ('На RTX 4090', '/catalog/servery-dlya-ii/na-rtx-4090/'), ('На RTX PRO 6000', '/catalog/servery-dlya-ii/na-rtx-pro-6000/'),
        ('HGX H100 и H200', '/catalog/servery-dlya-ii/hgx-h100-h200/')]),
    ('Фермы на видеокартах', '/catalog/mayning_fermy/', [('GPU-ферма для нейросетей', '/catalog/mayning_fermy/ferma-dlya-ii/'),
        ('Ферма на RTX 3090', '/catalog/mayning_fermy/na-rtx-3090/'), ('Фермы на NVIDIA', '/catalog/mayning_fermy/mayning_fermy_na_nvidia/'),
        ('Ферма для биткоина', '/catalog/mayning_fermy/dlya-bitkoina/'), ('Тушки без видеокарт', '/catalog/sborki-dlya-ii/platformy/')]),
    ('Видеокарты для ИИ', '/catalog/videokarty/', [('NVIDIA Tesla', '/catalog/videokarty/nvidia-tesla/'),
        ('RTX 3090', '/catalog/videokarty/rtx-3090/'), ('RTX 4090 48 ГБ', '/catalog/videokarty/rtx-4090-48gb/'),
        ('RTX 5090', '/catalog/videokarty/rtx-5090/'), ('RTX PRO 6000', '/catalog/videokarty/rtx-pro-6000/'),
        ('Серверные A100, H100, H200', '/catalog/videokarty/servernye/')]),
    ('Сборки и станции', '/catalog/sborki-dlya-ii/', [('Станция на 2 × RTX 3090', '/catalog/sborki-dlya-ii/2x-rtx-3090/'),
        ('Сервер на 4 × RTX 3090', '/catalog/sborki-dlya-ii/4x-rtx-3090/'), ('Домашний сервер для ИИ', '/catalog/sborki-dlya-ii/domashniy-server/'),
        ('NVIDIA DGX Spark', '/catalog/sborki-dlya-ii/nvidia-dgx-spark/')]),
    ('Комплектующие', '/catalog/komplektuyushchie/', [('Блоки питания', '/catalog/komplektuyushchie/bloki_pitaniya/'),
        ('Райзеры', '/catalog/komplektuyushchie/rayzery/'), ('Каркасы и корпуса', '/catalog/komplektuyushchie/korpusa_i_karkasy/'),
        ('Охлаждение Tesla', '/catalog/komplektuyushchie/okhlazhdenie-tesla/'), ('NVLink', '/catalog/komplektuyushchie/nvlink/')]),
    ('Асики и услуги', '/catalog/asic_maynery/', [('ASIC-майнеры', '/catalog/asic_maynery/'), ('Выкуп видеокарт', '/services/vykup-videokart/'),
        ('Трейд-ин', '/services/trade-in-videokart/'), ('Аренда GPU', '/services/arenda-gpu/'), ('Размещение в ЦОД', '/services/gpu-hosting/')]),
]


def header(path):
    # подсвечиваем один пункт — с самым длинным совпадающим префиксом
    cur = max((h for _, h in NAV if path.startswith(h)), key=len, default=None)
    nav = ''.join('<a href="%s"%s>%s</a>' % (u(h), ' aria-current="page"' if h == cur else '', t) for t, h in NAV)
    temp = ('<div class="temp-bar">Временная версия нового сайта MiningShop. Каталог и цены уточняйте у менеджера.</div>'
            if TEMPORARY else '')
    mega = ''.join('<div class="mega-col"><a class="mega-h" href="%s">%s</a>%s</div>'
                   % (u(h), t, ''.join('<a href="%s">%s</a>' % (u(sh), st) for st, sh in sub)) for t, h, sub in MEGA)
    top = ('<div class="topbar"><div class="wrap"><nav aria-label="Компания">'
           '<a href="%s">О компании</a><a href="%s">Доставка и оплата</a><a href="%s">Гарантия</a><a href="%s">Статьи</a><a href="%s">Контакты</a></nav>'
           '<div class="topbar-r"><a class="yt" href="%s" target="_blank" rel="noopener">%sYouTube-канал</a>'
           '<a class="tgc" href="%s" target="_blank" rel="noopener">%sКанал в Telegram</a></div></div></div>'
           % (u('/company/about/'), u('/company/delivery/'), u('/company/guarantee/'), u('/blog/'), u('/contacts/'),
              C['youtube'], icon('yt'), C['tg_channel'], icon('tg')))
    return (temp + top +
            '<header class="hdr"><div class="wrap">'
            '<a class="logo" href="%s" aria-label="MiningShop — на главную"><img src="%s" srcset="%s 2x" alt="MiningShop" width="175" height="34">'
            '<small>серверы, GPU-фермы и видеокарты для ИИ</small></a>'
            '<button class="btn btn-blue btn-sm mega-btn" type="button" aria-expanded="false" aria-controls="mega">%sКаталог</button>'
            '<form class="search" role="search" onsubmit="return false"><label class="sr" for="q">Поиск по сайту</label>'
            '<input id="q" type="search" placeholder="Поиск: RTX 3090, сервер для LLM, ферма…" autocomplete="off">'
            '%s<div class="search-res" hidden></div></form>'
            '<div class="hdr-contact"><a href="%s">%s</a><small>%s</small></div>'
            '<a class="btn btn-accent btn-sm hdr-cta" href="%s">Заказать звонок</a>'
            '<button class="burger" aria-controls="nav" aria-expanded="false" aria-label="Меню">%s</button>'
            '</div><div class="mega" id="mega" hidden><div class="wrap">%s</div></div>'
            '<div class="hdr-nav"><div class="wrap"><nav class="nav" id="nav">%s</nav></div></div></header>'
            % (u('/'), u('/assets/img/ui/logo.webp'), u('/assets/img/ui/logo@2x.webp'), icon('burger'), icon('search'),
               C['phone_href'], C['phone'], C['hours'], u('/contacts/#zvonok'), icon('burger'), mega, nav))


def footer():
    col = lambda title, links: '<div><h4>%s</h4>%s</div>' % (title, ''.join('<a href="%s">%s</a>' % (u(h), t) for t, h in links))
    return ('<footer class="ftr"><div class="wrap"><div class="ftr-grid">'
            '<div><h4>MiningShop</h4><p>Видеокарты, серверы и сборки для нейросетей с %d года: продаём, собираем, '
            'выкупаем и размещаем. Асики и майнинг-фермы — тоже к нам.</p>'
            '<a class="phone" href="%s">%s</a><a href="mailto:%s">%s</a><a href="%s">Telegram %s</a>'
            '<p style="margin:10px 0 0">%s<br>%s</p></div>'
            % (C['since'], C['phone_href'], C['phone'], C['email'], C['email'], C['tg'], C['tg_name'], C['address'], C['hours'])
            + col('Фермы и серверы', [('Фермы на видеокартах', '/catalog/mayning_fermy/'),
                                      ('GPU-ферма для нейросетей', '/catalog/mayning_fermy/ferma-dlya-ii/'),
                                      ('Ферма на RTX 3090', '/catalog/mayning_fermy/na-rtx-3090/'),
                                      ('Ферма для биткоина', '/catalog/mayning_fermy/dlya-bitkoina/'),
                                      ('Серверы для ИИ', '/catalog/servery-dlya-ii/'), ('Сервер для LLM', '/catalog/servery-dlya-ii/dlya-llm/'),
                                      ('Сервер для обучения', '/catalog/servery-dlya-ii/dlya-obucheniya/'),
                                      ('Серверы на 8 GPU', '/catalog/servery-dlya-ii/na-8-gpu/')])
            + col('Каталог', [('Видеокарты для ИИ', '/catalog/videokarty/'), ('Видеокарты NVIDIA', '/catalog/videokarty/videokarty_nvidia/'),
                              ('Tesla V100', '/catalog/videokarty/tesla-v100/'),
                              ('RTX 3090', '/catalog/videokarty/rtx-3090/'), ('RTX PRO 6000', '/catalog/videokarty/rtx-pro-6000/'),
                              ('Сборки и тушки', '/catalog/sborki-dlya-ii/'),
                              ('Комплектующие', '/catalog/komplektuyushchie/'), ('ASIC-майнеры', '/catalog/asic_maynery/')])
            + col('Услуги', [('Выкуп видеокарт', '/services/vykup-videokart/'), ('Трейд-ин видеокарт', '/services/trade-in-videokart/'),
                             ('Сборка сервера для ИИ', '/services/sborka-servera-dlya-ii/'), ('Аренда GPU', '/services/arenda-gpu/'),
                             ('Размещение GPU-серверов', '/services/gpu-hosting/'), ('Хостинг асиков', '/services/hosting/'),
                             ('Ремонт асиков', '/services/remont-oborudovaniya/')])
            + col('Компания', [('Калькулятор видеопамяти', '/calc/vram/'), ('Доходность асиков', '/table/'), ('Статьи', '/blog/'),
                               ('О компании', '/company/about/'), ('Доставка и оплата', '/company/delivery/'),
                               ('Гарантия', '/company/guarantee/'), ('Контакты', '/contacts/'), ('Политика конфиденциальности', '/privacy/'),
                               ('Пользовательское соглашение', '/terms/'), ('<b>Карта сайта</b>', '/karta-sajta/')])
            + '</div><div class="ftr-bottom"><span>© %d–2026 MiningShop. Информация на сайте не является публичной офертой.</span>'
              '<span>Расчёты доходности — ориентировочные, не инвестиционная рекомендация.</span></div></div></footer>' % C['since'])


ORG_LD = {
    "@type": "Organization", "@id": PROD + "/#org", "name": "MiningShop", "url": PROD + "/",
    "logo": PROD + "/assets/img/ui/logo@2x.webp", "email": C['email'], "telephone": "+7-999-499-96-96",
    "address": {"@type": "PostalAddress", "addressCountry": "RU", "addressLocality": "Москва",
                "streetAddress": "шоссе Энтузиастов, 56, стр. 20"},
    "sameAs": [C['tg']],
    "foundingDate": "2017",
    "description": "MiningShop — видеокарты, серверы и сборки для нейросетей с 2017 года: продажа, сборка, выкуп и трейд-ин видеокарт, "
                   "размещение GPU-серверов. Асики и майнинг-фермы.",
}


def crumbs_html(crumbs):
    parts = ['<a href="%s">Главная</a>' % u('/')]
    for i, (t, h) in enumerate(crumbs):
        parts.append('<span>/</span>' + ('<a href="%s">%s</a>' % (u(h), t) if i < len(crumbs) - 1 else t))
    return '<div class="crumbs">%s</div>' % ''.join(parts)


def crumbs_ld(crumbs):
    items = [{"@type": "ListItem", "position": 1, "name": "Главная", "item": PROD + "/"}]
    for i, (t, h) in enumerate(crumbs, 2):
        items.append({"@type": "ListItem", "position": i, "name": re.sub(r'<[^>]+>', '', t), "item": PROD + h})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def render(pg):
    """pg: path, title, description, body(html) и необязательные h1, lead, crumbs, hero(html), ld(list)."""
    path = pg['path']
    ld = [ORG_LD] + [x for x in pg.get('ld', []) if not (x.get('@type') == 'Product' and 'offers' not in x)]
    if pg.get('crumbs'):
        ld.append(crumbs_ld(pg['crumbs']))
    ld_json = json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False).replace('<', '\\u003c')

    if pg.get('hero') is not None:
        top = pg['hero']
    else:
        top = ('<section class="page-hero"><div class="wrap">%s<h1>%s</h1>%s</div></section>'
               % (crumbs_html(pg.get('crumbs', [])), pg['h1'], '<p>%s</p>' % pg['lead'] if pg.get('lead') else ''))

    robots = 'noindex, nofollow' if TEMPORARY else 'index, follow'
    head = (
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>%s</title><meta name="description" content="%s">'
        '<meta name="robots" content="%s">'
        '<link rel="canonical" href="%s">'
        '<meta property="og:type" content="website"><meta property="og:site_name" content="MiningShop">'
        '<meta property="og:title" content="%s"><meta property="og:description" content="%s">'
        '<meta property="og:url" content="%s"><meta property="og:locale" content="ru_RU">'
        '<meta name="theme-color" content="#ffffff">'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&family=Roboto:wght@400;500;700&display=swap">'
        '<link rel="stylesheet" href="%s">'
        '<link rel="icon" href="%s" type="image/png"><link rel="apple-touch-icon" href="%s">'
        '<script type="application/ld+json">%s</script>%s'
        '</head><body>'
        % (esc(pg['title']), esc(pg['description']), robots, PROD + path, esc(pg['title']), esc(pg['description']),
           PROD + path, u('/assets/site.css'), u('/assets/img/ui/favicon.png'), u('/assets/img/ui/apple-touch-icon.png'), ld_json, '' if TEMPORARY else METRIKA_JS))
    mbar = ('<nav class="mbar" aria-label="Связаться"><a href="%s">%sПозвонить</a><a href="%s">%sTelegram</a>'
            '<a class="go" href="%s">Подобрать</a></nav>' % (C['phone_href'], icon('phone'), C['tg'], icon('tg'), u('/#podbor')))
    head = head.replace('</head>', '<meta name="ms-base" content="%s"></head>' % BASE, 1)
    return (head + header(path) + '<main>' + top + pg['body'] + '</main>' + footer() + mbar
            + '<script src="%s" defer></script></body></html>' % u('/assets/site.js'))


PAGES = []


def add(**pg):
    assert pg['path'].startswith('/') and pg['path'].endswith('/'), pg['path']
    assert pg['path'] not in {x['path'] for x in PAGES}, 'дубль адреса ' + pg['path']
    PAGES.append(pg)
    return pg
