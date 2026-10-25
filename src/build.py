# -*- coding: utf-8 -*-
"""Сборка сайта в корень репозитория (GitHub Pages раздаёт его из ветки main).

    python3 src/build.py                                    # временный сайт на GitHub Pages: noindex, префикс /miningshop-site-v3
    MS_BASE= MS_TEMP=0 python3 src/build.py                 # боевая сборка для miningshop.ru: индексируется, .htaccess с редиректами

Боевую сборку выкладывать на хостинг целиком (вместе с .htaccess). Цены — src/data/prices.csv.
"""
import os, re, shutil, sys, html
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
import core
import pages_asic, pages_ai, pages_parts, pages_table, pages_blog, pages_buyback, pages_aiblog, pages_main  # noqa: F401  (регистрируют страницы)
import redirects

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT   # GitHub Pages раздаёт этот репозиторий из корня ветки main
KEEP = {'.git', '.gitignore', 'src', 'README.md'}   # всё остальное в корне — результат сборки

# ------------------------------------------------------------------ графика без внешних файлов
ASIC_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect width="400" height="300" fill="#f6f7f9"/>
<g transform="translate(70 70)"><rect width="260" height="160" rx="10" fill="#26313a"/><rect x="10" y="12" width="240" height="136" rx="6" fill="#1a232b"/>
%s<rect x="18" y="138" width="60" height="6" rx="3" fill="#fab432"/></g>
<text x="200" y="272" font-family="Roboto,Arial" font-size="15" fill="#66717c" text-anchor="middle">%s</text></svg>'''
FANS = '<circle cx="70" cy="80" r="48" fill="#11171c" stroke="#3a4650" stroke-width="3"/><circle cx="70" cy="80" r="10" fill="#3a4650"/>' \
       '<circle cx="190" cy="80" r="48" fill="#11171c" stroke="#3a4650" stroke-width="3"/><circle cx="190" cy="80" r="10" fill="#3a4650"/>'
HYDRO = '<rect x="40" y="40" width="180" height="80" rx="6" fill="#11171c"/><circle cx="70" cy="80" r="14" fill="#2b6cb0"/><circle cx="190" cy="80" r="14" fill="#c53030"/>' \
        '<rect x="84" y="76" width="92" height="8" fill="#3a4650"/>'
GPU_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"><rect width="400" height="300" fill="#f6f7f9"/>
<g transform="translate(50 95)"><rect width="300" height="100" rx="8" fill="#26313a"/><rect x="0" y="100" width="120" height="10" fill="#fab432"/>
<circle cx="90" cy="50" r="36" fill="#11171c" stroke="#3a4650" stroke-width="3"/><circle cx="210" cy="50" r="36" fill="#11171c" stroke="#3a4650" stroke-width="3"/>
<circle cx="90" cy="50" r="8" fill="#3a4650"/><circle cx="210" cy="50" r="8" fill="#3a4650"/></g>
<text x="200" y="262" font-family="Roboto,Arial" font-size="15" fill="#66717c" text-anchor="middle">GPU-ускоритель</text></svg>'''
HERO_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 700" preserveAspectRatio="xMidYMid slice">
<rect width="1600" height="700" fill="#11171c"/><g stroke="#26313a" stroke-width="2" fill="none">%s</g>
<g fill="#fab432" opacity=".55">%s</g></svg>'''
FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#11171c"/>' \
          '<path d="M7 23V9h4l5 7 5-7h4v14h-4v-8l-5 7-5-7v8z" fill="#fab432"/></svg>'


def hero_svg():
    lines, dots = [], []
    import random
    rnd = random.Random(7)
    for i in range(46):
        x, y = rnd.randrange(700, 1600, 40), rnd.randrange(0, 700, 40)
        w = rnd.choice([80, 120, 160, 240])
        lines.append('<path d="M%d %dh%dv%d"/>' % (x, y, w, rnd.choice([-80, 40, 80, 120])))
        dots.append('<circle cx="%d" cy="%d" r="3"/>' % (x, y))
    return HERO_SVG % (''.join(lines), ''.join(dots))


def write(rel, text):
    path = os.path.join(OUT, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def main():
    for name in os.listdir(OUT):
        if name not in KEEP:
            full = os.path.join(OUT, name)
            shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
    shutil.copytree(os.path.join(ROOT, 'src', 'static'), os.path.join(OUT, 'assets'))
    ui = 'assets/img/ui/'
    write(ui + 'asic-air.svg', ASIC_SVG % (FANS, 'ASIC-майнер, воздушное охлаждение'))
    write(ui + 'asic-hydro.svg', ASIC_SVG % (HYDRO, 'ASIC-майнер, гидроохлаждение'))
    write(ui + 'gpu.svg', GPU_SVG)
    write(ui + 'hero.svg', hero_svg())
    write(ui + 'favicon.svg', FAVICON)

    pages_blog.make_hub()
    for pg in core.PAGES:
        out = 'index.html' if pg['path'] == '/' else pg['path'].strip('/') + '/index.html'
        write(out, core.render(pg))
    # GitHub Pages показывает 404.html для несуществующих адресов
    shutil.copyfile(os.path.join(OUT, '404', 'index.html'), os.path.join(OUT, '404.html'))

    today = date.today().isoformat()
    urls = [pg['path'] for pg in core.PAGES if pg.get('kind') != 'system']
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join('<url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (core.PROD, x, today) for x in urls) + '</urlset>\n')
    if core.TEMPORARY:
        write('robots.txt', 'User-agent: *\nDisallow: /\n')   # временный сайт не должен попасть в индекс
    else:
        # ботов нейросетей не закрываем: сайт должен попадать в ответы Яндекс Нейро, ChatGPT, Perplexity, Claude
        write('robots.txt', 'User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /admin/\n\n'
              + ''.join('User-agent: %s\nAllow: /\n\n' % b for b in ('YandexBot', 'GPTBot', 'OAI-SearchBot', 'ChatGPT-User',
                                                                       'ClaudeBot', 'Claude-SearchBot', 'PerplexityBot', 'Google-Extended'))
              + 'Sitemap: %s/sitemap.xml\n' % core.PROD)

    # llms.txt — короткая карта сайта для нейросетей (https://llmstxt.org)
    def ln(path, text):
        return '- [%s](%s%s)' % (text, core.PROD, path)
    llm = ['# MiningShop', '',
           '> Магазин видеокарт, серверов и сборок для нейросетей в Москве, работает с 2017 года. Продаём видеокарты для ИИ '
           '(Tesla V100, P40, RTX 3090, 4090, 5090, RTX PRO 6000, A100, H100, H200), собираем станции и серверы под локальные '
           'LLM, выкупаем видеокарты и принимаем их в трейд-ин. Также ASIC-майнеры, майнинг-фермы и хостинг.', '',
           'Телефон: %s. Почта: %s. Telegram: %s. Адрес: %s.' % (core.C['phone'], core.C['email'], core.C['tg_name'], core.C['address']), '',
           '## Каталог', ln('/catalog/videokarty/', 'Видеокарты для ИИ'), ln('/catalog/servery-dlya-ii/', 'Серверы для ИИ'),
           ln('/catalog/sborki-dlya-ii/', 'Сборки для локального ИИ и платформы без видеокарт'),
           ln('/catalog/komplektuyushchie/', 'Комплектующие: NVLink, SXM2, охлаждение Tesla, райзеры, платы'),
           ln('/catalog/mayning_fermy/', 'Майнинг-фермы на видеокартах'), ln('/catalog/asic_maynery/', 'ASIC-майнеры'), '',
           '## Видеокарты'] + [ln(pages_ai.gpu_path(g), g['name'] + ' — ' + g['cls']) for g in pages_ai.G] + ['',
           '## Услуги', ln('/services/vykup-videokart/', 'Выкуп видеокарт'), ln('/services/trade-in-videokart/', 'Трейд-ин видеокарт'),
           ln('/services/sborka-servera-dlya-ii/', 'Сборка сервера для ИИ'), ln('/services/arenda-gpu/', 'Аренда GPU'),
           ln('/services/gpu-hosting/', 'Размещение GPU-серверов'), '',
           '## Справочные материалы', ln('/calc/vram/', 'Калькулятор видеопамяти для LLM')] + [
           ln(p_, h) for p_, h, _l, r in pages_blog.ARTICLES if r == 'ИИ и нейросети']
    write('llms.txt', '\n'.join(llm) + '\n')

    # товарный фид YML для Авито (автозагрузка), Яндекс Маркета и товаров в поиске — только позиции с ценой
    offers = []
    for g in pages_ai.G:
        for i, r in enumerate(pages_ai.PRICES.get(g['key'], [])):
            if (r.get('price_rub') or '').strip().isdigit():
                offers.append('<offer id="%s-%d" available="%s"><url>%s%s</url><price>%s</price><currencyId>RUR</currencyId>'
                              '<categoryId>1</categoryId><name>%s %s</name><vendor>%s</vendor><description>%s</description></offer>'
                              % (g['key'], i + 1, 'true' if 'налич' in (r.get('stock') or '') else 'false', core.PROD, pages_ai.gpu_path(g),
                                 r['price_rub'].strip(), html.escape(g['name']), html.escape(r['variant']),
                                 'AMD' if g['fam'] == 'amd' else 'NVIDIA', html.escape(g['cls'] + '. ' + g['use'])))
    write('feed.yml', '<?xml version="1.0" encoding="UTF-8"?>\n<yml_catalog date="%s"><shop><name>MiningShop</name>'
          '<company>MiningShop</company><url>%s/</url><currencies><currency id="RUR" rate="1"/></currencies>'
          '<categories><category id="1">Видеокарты</category></categories><offers>%s</offers></shop></yml_catalog>\n'
          % (today, core.PROD, ''.join(offers)))

    # редиректы со старого сайта: список для проверки и .htaccess для боевого хостинга (Apache на Beget)
    rules = redirects.build({pg['path'] for pg in core.PAGES})
    write('redirects.csv', 'old;new\n' + ''.join('%s;%s\n' % r for r in rules))
    if not core.TEMPORARY:
        write('.htaccess', redirects.htaccess(rules, core.PROD))
    print('редиректов со старого сайта: %d, товаров в фиде: %d' % (len(rules), len(offers)))
    write('.nojekyll', '')

    # ---- проверки качества
    problems = []
    titles, descs = {}, {}
    for pg in [x for x in core.PAGES if x.get('kind') != 'system']:
        titles.setdefault(pg['title'], []).append(pg['path'])
        descs.setdefault(pg['description'], []).append(pg['path'])
        if len(pg['title']) > 90:
            problems.append('длинный title (%d): %s' % (len(pg['title']), pg['path']))
        if not (70 <= len(pg['description']) <= 260):
            problems.append('description %d зн.: %s' % (len(pg['description']), pg['path']))
    problems += ['дубль title: %s' % v for v in titles.values() if len(v) > 1]
    problems += ['дубль description: %s' % v for v in descs.values() if len(v) > 1]

    known = {pg['path'] for pg in core.PAGES}
    broken = {}
    for pg in core.PAGES:
        page_html = open(os.path.join(OUT, ('index.html' if pg['path'] == '/' else pg['path'].strip('/') + '/index.html')
                                      .replace('/', os.sep)), encoding='utf-8').read()
        if page_html.count('<h1') != 1:
            problems.append('h1 x%d: %s' % (page_html.count('<h1'), pg['path']))
        for href in re.findall(r'(?:href|src)="(%s/[^"#?]*)' % re.escape(core.BASE), page_html):
            rel = href[len(core.BASE):] or '/'
            if rel.startswith('/assets/'):
                if not os.path.exists(os.path.join(OUT, rel.strip('/').replace('/', os.sep))):
                    broken.setdefault(rel, set()).add(pg['path'])
            elif rel not in known:
                broken.setdefault(rel, set()).add(pg['path'])
    words = sum(len(re.sub(r'<[^>]+>', ' ', pg['body']).split()) for pg in core.PAGES)
    print('страниц: %d, слов в теле страниц: ~%d' % (len(core.PAGES), words))
    print('битых внутренних ссылок: %d' % len(broken))
    for k, v in list(broken.items())[:20]:
        print('   %s  <- %s' % (k, sorted(v)[:2]))
    print('замечаний SEO: %d' % len(problems))
    for x in problems[:30]:
        print('   ' + x)
    return 1 if broken else 0


if __name__ == '__main__':
    sys.exit(main())
