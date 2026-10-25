# -*- coding: utf-8 -*-
"""Главная, каталог, услуги, консультация и страницы компании."""
import json, os, re
from core import (add, u, esc, h2, h3, p, ul, ol, note, ptable, faq_html, faq_ld, cards, section, cta_box, a, steps, icon, C)
from pages_asic import M, card as asic_card, eff
from pages_ai import G, GK, gpu_card, grid, size_table
from pages_buyback import SERVICES_EXTRA
from pages_blog import fix_links, REUSED

# ================================================================== опросник подбора
QUIZ = [
    ('Что нужно?', [('Видеокарта для ИИ', 'одна или несколько карт'), ('Станция или сервер для ИИ', 'готовая сборка под модель'),
                    ('Продать или обменять карты', 'выкуп и трейд-ин'), ('Асики и майнинг', 'ASIC, фермы, хостинг')], False),
    ('Что будете запускать?', [('Чат-модели (LLM)', 'Qwen, DeepSeek, Llama'), ('Генерация изображений и видео', 'ComfyUI, Flux'),
                               ('Обучение и дообучение', 'LoRA, полное обучение'), ('Пока не знаю', 'поможем разобраться')], False),
    ('Бюджет', [('До 300 тыс. ₽', 'Tesla P40, RTX 3090'), ('300 тыс. – 1 млн ₽', 'RTX 4090/5090, 2–4 карты'),
                ('1–5 млн ₽', 'RTX PRO 6000, серверы 4–8 GPU'), ('Больше 5 млн ₽', 'A100, H100, H200')], False),
    ('Что важно? (можно несколько)', [('Скорость ответа', ''), ('Тишина, работа в офисе', ''), ('Сдать старые карты в зачёт', ''),
                                       ('Размещение в дата-центре', '')], True),
]


def quiz_html():
    steps_html = ''
    for i, (q, opts, multi) in enumerate(QUIZ):
        t = 'checkbox' if multi else 'radio'
        steps_html += ('<fieldset class="quiz-step"%s><legend>%s</legend><div class="opts">%s</div></fieldset>'
                       % ('' if i == 0 else ' hidden', q, ''.join(
                           '<label class="opt"><input type="%s" name="q%d" value="%s"><span>%s%s</span></label>'
                           % (t, i, esc(o), o, '<small>%s</small>' % d if d else '') for o, d in opts)))
    steps_html += ('<fieldset class="quiz-step" hidden><legend>Куда прислать подбор?</legend>'
                   '<p style="margin:0 0 12px;color:#66717c">Выберите удобный способ — откроется Telegram или почта с уже заполненным текстом.</p>'
                   '<div class="quiz-result"></div>'
                   '<label class="field"><span>Комментарий (модель, карты, которые хотите сдать, — что знаете)</span><textarea name="note" rows="3"></textarea></label>'
                   '<div class="pd-actions"><a class="btn btn-accent" data-tg href="%s" target="_blank" rel="noopener">Отправить в Telegram</a>'
                   '<a class="btn btn-line" data-mail href="mailto:%s">Отправить на почту</a>'
                   '<a class="btn btn-line" href="%s">Позвонить %s</a></div></fieldset>'
                   % (C['tg'], C['email'], C['phone_href'], C['phone']))
    return ('<div class="quiz" data-quiz><div class="quiz-side"><div class="avatar">%s</div>'
            '<h3>Подберём железо под вашу нейросеть</h3><p>Ответьте на 4 вопроса — предложим 2–3 варианта: видеокарты, '
            'сборку или сервер, с ценой и сроками.</p><p>%s<br>%s</p></div>'
            '<div class="quiz-main"><div class="progress"><i></i></div><div class="step-label"></div>%s'
            '<div class="quiz-nav"><button class="btn btn-line" type="button" data-prev>Назад</button>'
            '<button class="btn btn-accent" type="button" data-next>Далее</button></div></div></div>'
            % (icon('user'), C['phone'], C['hours'], steps_html))


# ================================================================== главная
TOP = ['tesla-v100', 'rtx-pro-6000', 'rtx-3090', 'tesla-p40', 'rtx-4090-48gb', 'rtx-5090', 'a100', 'h200']
home_faq = [
    ('Какая видеокарта нужна для нейросетей?',
     'Главное — объём видеопамяти. 24 ГБ (RTX 3090, 4090, Tesla P40) хватает для моделей до 30 млрд параметров, 48 ГБ '
     '(RTX A6000, RTX 4090 48 ГБ) — до 70 млрд, для крупных моделей нужны RTX PRO 6000 или серверы на A100, H100, H200. '
     'Подробнее — <a href="%s">какую видеокарту выбрать для ИИ</a>.' % u('/blog/videokarta-dlya-ii/')),
    ('Собираете готовые станции и серверы?',
     'Да. С 2017 года мы собирали фермы на видеокартах, теперь собираем станции и серверы для нейросетей: подбираем карты под '
     'модель, ставим софт и тестируем под нагрузкой — <a href="%s">сборки для ИИ</a>.' % u('/catalog/sborki-dlya-ii/')),
    ('Покупаете старые видеокарты?',
     'Да: рабочие, после майнинга и нерабочие, а также Tesla, серверы и фермы целиком. Можно продать или засчитать в покупку — '
     '<a href="%s">выкуп</a> и <a href="%s">трейд-ин</a>.' % (u('/services/vykup-videokart/'), u('/services/trade-in-videokart/'))),
    ('Почему у многих позиций цена по запросу?',
     'Цены на видеокарты и серверные GPU меняются почти каждый день и зависят от партии. Называем актуальную цену в момент '
     'запроса и фиксируем её в счёте.'),
    ('Асики у вас тоже есть?',
     'Да, каталог ASIC-майнеров, хостинг и ремонт остаются: <a href="%s">асики</a> и <a href="%s">калькулятор доходности</a>.'
     % (u('/catalog/asic_maynery/'), u('/table/'))),
]

hero = ('<section class="hero" style="background-image:url(%s)"><div class="wrap">'
        '<h1>Видеокарты, серверы и сборки <em>для нейросетей</em> — с 2017 года</h1>'
        '<p class="lead">Tesla V100 и P40, RTX 3090–5090, RTX PRO 6000, A100, H100, H200. Подбираем под вашу модель, собираем '
        'станции и серверы, выкупаем старые карты в зачёт.</p>'
        '<div class="actions"><a class="btn btn-accent" href="%s">Подобрать под задачу</a>'
        '<a class="btn btn-ghost" href="%s">Сдать видеокарту</a></div>'
        '<div class="stats"><div><b>с 2017</b><span>работаем с видеокартами: начинали с ферм</span></div>'
        '<div><b>%d</b><span>моделей видеокарт для ИИ — от Tesla P40 до H200</span></div>'
        '<div><b>24 ч</b><span>тест каждой сборки под нагрузкой перед отправкой</span></div>'
        '<div><b>1 день</b><span>на оценку карт для выкупа и трейд-ина</span></div></div>'
        '</div></section>' % (u('/assets/img/ui/hero.svg'), u('/#podbor'), u('/services/vykup-videokart/'), len(G)))

home_body = (
    section(cards([
        ('chip', 'Видеокарты для ИИ', 'Tesla, RTX, профессиональные и серверные — новые и б/у с проверкой.', '/catalog/videokarty/'),
        ('box', 'Сборки и тушки', 'Станции на 2–4 карты, домашний сервер для ИИ, платформы без карт.', '/catalog/sborki-dlya-ii/'),
        ('server', 'Серверы для ИИ', 'GPU-серверы 4U, Tesla V100 SXM2, HGX H100/H200 и B200/B300.', '/catalog/servery-dlya-ii/'),
        ('calc', 'Выкуп и трейд-ин', 'Продайте старые карты или засчитайте их в покупку.', '/services/vykup-videokart/'),
    ], 4), cls='sec-soft', title='Что мы делаем',
        sub='Магазин видеокарт с 2017 года. Раньше — фермы для майнинга, сегодня — железо для нейросетей.')
    + section(grid([GK[k] for k in TOP]) + '<p style="margin:24px 0 0"><a class="btn btn-line" href="%s">Все видеокарты для ИИ</a></p>'
              % u('/catalog/videokarty/'), title='Популярные видеокарты для ИИ',
              sub='Самые частые запросы: Tesla V100, RTX PRO 6000, RTX 3090. Цена и наличие — на странице модели.')
    + section('<div class="prose" style="max-width:1000px">' + h2('Сколько видеопамяти нужно', 'pamyat')
              + p('Модель должна целиком поместиться в память видеокарт. Ориентир — в таблице, точнее — в '
                  + a('/calc/vram/', 'калькуляторе видеопамяти') + '.') + size_table() + '</div>', cls='sec-soft')
    + section(quiz_html(), title='Подбор под задачу', anchor='podbor',
              sub='Ответьте на 4 вопроса — предложим 2–3 варианта с ценой и сроками.')
    + section('<div class="banner"><div><h2>Сдайте старые карты в зачёт</h2><p>Выкупаем видеокарты после майнинга и игр, Tesla, '
              'серверы и фермы целиком. Оценка за рабочий день, оплата сразу после проверки, а при обмене — цена выше.</p></div>'
              '<a class="btn" href="%s">Оценить карты</a></div>' % u('/services/vykup-videokart/'))
    + section(cards([(ic, t, d, h) for ic, t, d, h in SERVICES_EXTRA] + [
        ('server', 'Размещение GPU-серверов', 'Серверы в дата-центре с резервным питанием.', '/services/gpu-hosting/')], 3),
        cls='sec-soft', title='Услуги')
    + section(cards([
        (None, 'Какую видеокарту выбрать для ИИ', 'Лучшие карты по бюджету и что на них запускается.', '/blog/videokarta-dlya-ii/'),
        (None, 'Сколько видеопамяти нужно', 'Формула и таблица для моделей 7–235 млрд параметров.', '/blog/skolko-vram-nuzhno/'),
        (None, 'Tesla P40, P100, V100 и K80', 'Какую старую Tesla взять для нейросетей.', '/blog/tesla-p40-vs-v100/'),
    ], 3) + '<p style="margin:24px 0 0"><a class="btn btn-line" href="%s">Все статьи</a></p>' % u('/blog/'),
        title='Статьи и руководства')
    + section(cards([
        ('chip', 'ASIC-майнеры', 'Antminer S21, Whatsminer и другие — с расчётом окупаемости.', '/catalog/asic_maynery/'),
        ('bolt', 'Майнинг-фермы', 'Сборка ферм и перевод под нейросети.', '/catalog/mayning_fermy/'),
        ('chart', 'Доходность асиков', 'Калькулятор окупаемости на вашем тарифе.', '/table/'),
    ], 3), title='Майнинг', sub='С майнинга мы начинали — асики, фермы и сервис никуда не делись.')
    + section('<div style="max-width:880px">' + faq_html(home_faq) + '</div>', cls='sec-soft', title='Частые вопросы')
    + section('<div class="grid g2"><div class="contact-list">'
              '<div><div class="ico">%s</div><div><b>Телефон, бесплатно по России</b><a href="%s">%s</a></div></div>'
              '<div><div class="ico">%s</div><div><b>Почта</b><a href="mailto:%s">%s</a></div></div>'
              '<div><div class="ico">%s</div><div><b>Telegram</b><a href="%s">%s</a></div></div></div>'
              '<div class="card"><h3>Офис в Москве</h3><p>%s<br>%s</p><p style="margin-top:16px"><a class="btn btn-line btn-sm" href="%s">Все контакты</a></p></div></div>'
              % (icon('phone'), C['phone_href'], C['phone'], icon('mail'), C['email'], C['email'], icon('tg'), C['tg'], C['tg_name'],
                 C['address'], C['hours'], u('/contacts/')), title='Контакты')
)
add(path='/', kind='home',
    title='MiningShop — видеокарты, серверы и сборки для нейросетей с 2017 года',
    description='Видеокарты для ИИ (Tesla V100, P40, RTX 3090, 4090, 5090, RTX PRO 6000, A100, H100, H200), сборки и серверы '
                'для нейросетей, выкуп и трейд-ин видеокарт. Москва и вся Россия, с 2017 года.',
    h1='', hero=hero, body=home_body,
    ld=[faq_ld(home_faq), {"@type": "WebSite", "name": "MiningShop", "url": "https://miningshop.ru/"},
        {"@type": "Store", "name": "MiningShop", "url": "https://miningshop.ru/", "parentOrganization": {"@id": "https://miningshop.ru/#org"},
         "telephone": "+7-800-200-32-64", "address": {"@type": "PostalAddress", "addressCountry": "RU", "addressLocality": "Москва",
                                                     "streetAddress": "шоссе Энтузиастов, 56, стр. 20"}}])

# ================================================================== каталог
add(path='/catalog/', kind='hub', title='Каталог: видеокарты и серверы для ИИ, сборки, комплектующие, асики — MiningShop',
    description='Видеокарты и серверы для нейросетей, сборки и тушки, комплектующие для GPU-серверов, майнинг-фермы и '
                'ASIC-майнеры. Подбор под задачу.',
    h1='Каталог', lead='Железо для нейросетей и майнинга: подберём под задачу и бюджет.',
    crumbs=[('Каталог', '/catalog/')],
    body=section(cards([
        ('chip', 'Видеокарты для ИИ', '%d моделей: Tesla, RTX, профессиональные и серверные.' % len(G), '/catalog/videokarty/'),
        ('server', 'Серверы для ИИ', 'GPU-серверы на 4–8 карт, HGX H100/H200, B200/B300.', '/catalog/servery-dlya-ii/'),
        ('box', 'Сборки и тушки', 'Станции на 2–4 карты, домашние серверы, платформы без карт.', '/catalog/sborki-dlya-ii/'),
        ('fan', 'Комплектующие', 'NVLink, SXM2, охлаждение Tesla, райзеры, платы, БП.', '/catalog/komplektuyushchie/'),
        ('bolt', 'Майнинг-фермы', 'Сборка ферм и перевод под ИИ.', '/catalog/mayning_fermy/'),
        ('chip', 'ASIC-майнеры', '%d моделей: Antminer, Whatsminer, iPollo, Jasminer.' % len(M), '/catalog/asic_maynery/'),
    ], 3), cls='sec-soft'))

# ================================================================== услуги (тексты с текущего сайта)
SRV_ICON = {'hosting': 'server', 'gpu-hosting': 'chip', 'remont-oborudovaniya': 'wrench', 'mining-pod-kljuch': 'bolt',
            'business-plan': 'doc', 'proektirovanie-stroitelstvo-data-centrov': 'box'}
srv_cards = []
for s in REUSED['services']:
    path = s['url']
    key = path.strip('/').split('/')[-1]
    faq = s.get('faq') or []
    body_html = fix_links(''.join(s['body']))
    if faq:
        body_html += h2('Частые вопросы', 'faq') + faq_html(faq)
    body = section('<div class="layout"><div><div class="prose">' + body_html + '</div></div><aside class="aside">'
                   + '<nav class="toc"><b>Содержание</b>%s</nav>' % ''.join('<a href="#%s">%s</a>' % (anc, t) for t, anc in s['toc'])
                   + cta_box('Обсудим задачу', 'Расскажите о задаче — подготовим расчёт и предложение.', '/#podbor', 'Оставить заявку')
                   + '</aside></div>')
    title = s['title'].replace(' | MiningShop', ' — MiningShop')
    add(path=path, kind='service', title=title, description=s['description'], h1=s['h1'], lead=s['lead'],
        crumbs=[('Услуги', '/services/'), (s['h1'], path)], body=body,
        ld=[{"@type": "Service", "name": s['h1'], "description": s['description'], "areaServed": "RU",
             "provider": {"@id": "https://miningshop.ru/#org"}}] + ([faq_ld(faq)] if faq else []))
    srv_cards.append((SRV_ICON.get(key, 'wrench'), s['h1'], s['description'].split('.')[0] + '.', path))

add(path='/services/', kind='hub', title='Услуги: выкуп и трейд-ин видеокарт, сборка серверов для ИИ, аренда GPU — MiningShop',
    description='Выкуп и трейд-ин видеокарт, сборка серверов для ИИ, аренда GPU, размещение GPU-серверов и асиков, ремонт, '
                'запуск под ключ, проектирование дата-центров.',
    h1='Услуги', lead='Выкуп и обмен видеокарт, сборка и размещение серверов для ИИ, обслуживание асиков — от одной карты до дата-центра.',
    crumbs=[('Услуги', '/services/')], body=section(cards(SERVICES_EXTRA + srv_cards, 3), cls='sec-soft'))

# ================================================================== консультация (живой адрес)
add(path='/consulting/', kind='page', title='Консультация по оборудованию для майнинга и ИИ — MiningShop',
    description='Бесплатная консультация: подбор асика или GPU под тариф и задачу, расчёт окупаемости, выбор размещения.',
    h1='Консультация', lead='Подбор оборудования, расчёт окупаемости и выбор размещения — расскажите о задаче.',
    crumbs=[('Консультация', '/consulting/')],
    body=section(quiz_html(), cls='sec-soft')
    + section('<div class="prose">' + h2('С чем приходят за консультацией')
              + ul(['Какой асик окупится на моём тарифе?', 'Что выгоднее: дома, на своей площадке или в дата-центре?',
                    'Какой GPU или сервер нужен под мою нейросеть?', 'Стоит ли ремонтировать старое оборудование?',
                    'Как посчитать проект майнинг-фермы или площадки под ИИ?'])
              + h2('Что подготовить') + ul(['Тариф на электроэнергию и доступную мощность.', 'Помещение: вентиляция, шум, соседи.',
                                            'Бюджет и горизонт проекта.', 'Если оборудование уже есть — модели и показатели.'])
              + note('Честно о главном', 'Доход от майнинга зависит от курса и сложности сети, которые никто не прогнозирует. Мы '
                     'считаем то, что можно посчитать: расходы, себестоимость и запас прочности.') + '</div>'))

# ================================================================== о компании
add(path='/company/about/', kind='page', title='О компании MiningShop — оборудование для майнинга и ИИ с 2017 года',
    description='MiningShop работает с 2017 года: продажа, настройка, ремонт и размещение майнингового оборудования, '
                'а теперь и серверов для ИИ.',
    h1='О компании', lead='С 2017 года продаём, настраиваем и обслуживаем оборудование для майнинга. Теперь — и для вычислений ИИ.',
    crumbs=[('О компании', '/company/about/')],
    body=section('<div class="prose">'
                 + h2('История')
                 + p('MiningShop начал работу в мае 2017 года с продажи видеокарт для майнинга. Через несколько месяцев в '
                     'ассортименте появились готовые майнинг-фермы, затем — ASIC-майнеры. За это время мы прошли с клиентами '
                     'несколько циклов рынка: бум 2017-го, крипто-зиму 2018-го, рекордный 2021 год и переход Ethereum на '
                     'Proof-of-Stake в 2022-м.')
                 + p('Сегодня рынок снова меняется: майнинг на видеокартах уступил место асикам, а сами видеокарты стали нужны '
                     'для вычислений ИИ. Поэтому мы работаем по двум направлениям — майнинг биткоина и других монет на асиках '
                     'и оборудование для нейросетей.')
                 + h2('Что мы делаем')
                 + ul(['Подбираем ' + a('/catalog/asic_maynery/', 'ASIC-майнеры') + ' и ' + a('/catalog/videokarty/', 'GPU для ИИ') +
                       ' под задачу и тариф — с расчётом окупаемости до покупки.',
                       'Доставляем по России, запускаем и настраиваем оборудование.',
                       'Ремонтируем асики: хешплаты, блоки питания, платы управления.',
                       'Размещаем оборудование в дата-центрах и запускаем площадки под ключ.'])
                 + h2('Принципы')
                 + ul(['<b>Сначала расчёт.</b> Показываем экономику на вашем тарифе до покупки.',
                       '<b>Не обещаем доход.</b> Курс и сложность сети не прогнозируются — говорим о рисках прямо.',
                       '<b>Актуальная цена.</b> Не держим на сайте устаревшие цифры — называем цену в момент запроса.'])
                 + '</div>'))

# ================================================================== контакты
map_link = 'https://yandex.ru/maps/?text=' + 'Москва, шоссе Энтузиастов, 56с20'
add(path='/contacts/', kind='page', title='Контакты MiningShop: телефон 8 (800) 200-32-64, офис в Москве',
    description='Связаться с MiningShop: телефон 8 (800) 200-32-64 (бесплатно по России), info@miningshop.ru, Telegram @miningshop. '
                'Офис: Москва, шоссе Энтузиастов, 56, стр. 20.',
    h1='Контакты', lead='Ответим на вопросы о подборе, доставке, настройке и размещении оборудования.',
    crumbs=[('Контакты', '/contacts/')],
    body=section('<div class="grid g2"><div class="contact-list">'
                 '<div><div class="ico">%s</div><div><b>Телефон, бесплатно по России</b><a href="%s">%s</a></div></div>'
                 '<div><div class="ico">%s</div><div><b>Почта</b><a href="mailto:%s">%s</a></div></div>'
                 '<div><div class="ico">%s</div><div><b>Telegram</b><a href="%s">%s</a></div></div>'
                 '<div><div class="ico">%s</div><div><b>Режим работы</b><span>%s, сб–вс — выходной</span></div></div></div>'
                 '<div class="card"><h3>Офис</h3><p>%s</p><p style="margin-top:14px"><a class="btn btn-line btn-sm" href="%s" target="_blank" rel="noopener">Открыть на Яндекс Картах</a></p>'
                 '<h3 style="margin-top:28px">Реквизиты</h3><p>Реквизиты для договора и выставления счёта направим по запросу на '
                 '<a href="mailto:%s">%s</a>.</p></div></div>'
                 % (icon('phone'), C['phone_href'], C['phone'], icon('mail'), C['email'], C['email'], icon('tg'), C['tg'], C['tg_name'],
                    icon('calc'), C['hours'], C['address'], map_link, C['email'], C['email']), cls='sec-soft')
    + section(quiz_html(), title='Подбор оборудования'),
    ld=[{"@type": "ContactPage", "name": "Контакты MiningShop", "url": "https://miningshop.ru/contacts/"}])

# ================================================================== доставка, гарантия, политика
add(path='/company/delivery/', kind='page', title='Доставка и оплата оборудования для майнинга — MiningShop',
    description='Доставка асиков и видеокарт по России, самовывоз из офиса в Москве, приёмка оборудования, способы оплаты.',
    h1='Доставка и оплата', lead='Отправляем оборудование по России. Условия, сроки и стоимость доставки рассчитываем под заказ.',
    crumbs=[('Доставка и оплата', '/company/delivery/')],
    body=section('<div class="prose">'
                 + h2('Доставка') + p('Отправляем оборудование по России транспортными компаниями. Стоимость и сроки зависят от '
                                      'региона, веса и количества устройств — рассчитаем при оформлении заказа.')
                 + p('Самовывоз возможен из офиса в Москве: ' + C['address'] + ' — по предварительной договорённости.')
                 + h2('Как принять оборудование') + ol(
                     ['Осмотрите упаковку при получении: следы ударов и вскрытия фиксируйте в акте с перевозчиком.',
                      'Сверьте серийные номера с документами.', 'Если оборудование приехало с мороза, дайте ему прогреться 3–4 часа до включения.',
                      'Запустите и проверьте хешрейт по ' + a('/blog/poleznye-materialy/asik-rukovodstvo-polzovatelya/', 'руководству') + '.'])
                 + h2('Оплата') + p('Работаем с юридическими лицами и ИП по безналичному расчёту. Способы оплаты для частных лиц '
                                    'уточняйте у менеджера. Цена фиксируется в счёте на момент оформления.')
                 + note('Условия уточняйте', 'Точные условия доставки и оплаты для вашего заказа сообщит менеджер: '
                        + '<a href="%s">%s</a>, <a href="mailto:%s">%s</a>.' % (C['phone_href'], C['phone'], C['email'], C['email']))
                 + '</div>'))

add(path='/company/guarantee/', kind='page', title='Гарантия на асики и оборудование — MiningShop',
    description='Гарантия на майнинговое оборудование: гарантия производителя, проверка перед отправкой, что делать при неисправности.',
    h1='Гарантия', lead='Как работает гарантия на асики и видеокарты и что делать, если оборудование неисправно.',
    crumbs=[('Гарантия', '/company/guarantee/')],
    body=section('<div class="prose">'
                 + h2('Гарантия производителя') + p('На новое оборудование действует гарантия производителя. Её срок и условия '
                                                    'зависят от модели и указываются при оформлении заказа.')
                 + h2('Что не покрывается гарантией') + ul(['Самостоятельное вскрытие и ремонт.', 'Установка неофициальной прошивки.',
                                                            'Повреждения от перенапряжения, влаги и конденсата.', 'Механические повреждения.'])
                 + h2('Если оборудование неисправно') + ol(['Проверьте типовые причины по ' + a('/blog/poleznye-materialy/ustanovka-remont-i-diagnostika-asic-maynerov-kak-obespechit-bespereboynuyu-rabotu-vashey-mayning-fer/', 'руководству по диагностике') + '.',
                                                           'Сохраните лог и снимки веб-интерфейса.',
                                                           'Свяжитесь с нами — подскажем порядок обращения и организуем диагностику.'])
                 + p('Для оборудования вне гарантии — ' + a('/services/remont-oborudovaniya/', 'платный ремонт') + '.')
                 + '</div>'))

add(path='/privacy/', kind='page', title='Политика конфиденциальности — MiningShop',
    description='Политика обработки персональных данных MiningShop: какие данные мы получаем через сайт, зачем и как их можно удалить.',
    h1='Политика конфиденциальности', lead='Какие данные мы получаем через сайт и как их используем.',
    crumbs=[('Политика конфиденциальности', '/privacy/')],
    body=section('<div class="prose">'
                 + p('Настоящая политика описывает обработку персональных данных посетителей сайта miningshop.ru в соответствии '
                     'с Федеральным законом № 152-ФЗ «О персональных данных».')
                 + h2('Какие данные мы получаем') + ul(['Данные, которые вы сами сообщаете при обращении: имя, телефон, почта, '
                                                         'содержание запроса.', 'Технические данные посещения: IP-адрес, тип браузера, '
                                                         'страницы сайта — через сервис веб-аналитики.'])
                 + h2('Зачем') + ul(['Чтобы ответить на обращение и подготовить предложение.', 'Чтобы улучшать сайт.'])
                 + h2('Передача третьим лицам') + p('Мы не передаём персональные данные третьим лицам, кроме случаев, предусмотренных '
                                                   'законом, и случаев, необходимых для исполнения вашего заказа (например, доставки).')
                 + h2('Ваши права') + p('Вы можете запросить сведения о своих данных, их изменение или удаление, написав на '
                                        '<a href="mailto:%s">%s</a>.' % (C['email'], C['email']))
                 + '</div>'))

# ================================================================== 404
add(path='/404/', kind='system', title='Страница не найдена — MiningShop', description='Такой страницы нет.',
    h1='Страница не найдена', lead='Адрес указан с ошибкой или страница переехала. Основные разделы:',
    crumbs=[('404', '/404/')],
    body=section(cards([
        ('chip', 'ASIC-майнеры', 'Каталог асиков.', '/catalog/asic_maynery/'),
        ('server', 'Видеокарты для ИИ', 'Tesla, RTX, серверные GPU.', '/catalog/videokarty/'),
        ('calc', 'Выкуп видеокарт', 'Продать или обменять карты.', '/services/vykup-videokart/'),
        ('chart', 'Доходность', 'Калькулятор окупаемости.', '/table/'),
    ], 3), cls='sec-soft'))
