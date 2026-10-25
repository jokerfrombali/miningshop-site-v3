/* MiningShop — поведение страниц без сторонних библиотек. */
(function () {
  'use strict';

  // --- мобильное меню ---
  var burger = document.querySelector('.burger');
  var nav = document.querySelector('.nav');
  if (burger && nav) {
    burger.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // --- галерея на карточке товара ---
  document.querySelectorAll('.thumbs button').forEach(function (b) {
    b.addEventListener('click', function () {
      var main = b.closest('.pd-gallery').querySelector('.main img');
      if (main) { main.src = b.dataset.src; }
    });
  });

  // --- фильтр каталога по брендам/алгоритмам ---
  document.querySelectorAll('[data-filter-group]').forEach(function (group) {
    var target = document.querySelector(group.dataset.filterGroup);
    if (!target) return;
    group.querySelectorAll('.chip').forEach(function (chip) {
      chip.addEventListener('click', function () {
        group.querySelectorAll('.chip').forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
        chip.setAttribute('aria-pressed', 'true');
        var v = chip.dataset.value;
        target.querySelectorAll('[data-tags]').forEach(function (el) {
          el.hidden = v !== 'all' && el.dataset.tags.split(' ').indexOf(v) === -1;
        });
      });
    });
  });

  // --- опросник подбора оборудования ---
  // Сайт временный и без сервера, поэтому заявка не «отправляется в пустоту»:
  // собираем текст и честно предлагаем отправить его в Telegram или на почту.
  var quiz = document.querySelector('[data-quiz]');
  if (quiz) {
    var steps = Array.prototype.slice.call(quiz.querySelectorAll('.quiz-step'));
    var bar = quiz.querySelector('.progress i');
    var label = quiz.querySelector('.step-label');
    var prev = quiz.querySelector('[data-prev]');
    var next = quiz.querySelector('[data-next]');
    var i = 0;
    function show(n) {
      i = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      bar.style.width = ((i + 1) / steps.length * 100) + '%';
      label.textContent = 'Шаг ' + (i + 1) + ' из ' + steps.length;
      prev.hidden = i === 0;
      next.hidden = i === steps.length - 1;
      if (i === steps.length - 1) { summary(); }
    }
    function summary() {
      var lines = [];
      steps.slice(0, -1).forEach(function (s) {
        var q = s.querySelector('legend').textContent;
        var a = Array.prototype.slice.call(s.querySelectorAll('input:checked')).map(function (x) { return x.value; });
        if (a.length) lines.push(q + ': ' + a.join(', '));
      });
      var text = 'Заявка с сайта MiningShop\n' + lines.join('\n');
      var out = quiz.querySelector('.quiz-result');
      out.textContent = text;
      var note = quiz.querySelector('[name=note]');
      function build() {
        var full = text + (note && note.value ? '\nКомментарий: ' + note.value : '');
        quiz.querySelector('[data-tg]').href = 'https://t.me/miningshop?text=' + encodeURIComponent(full);
        quiz.querySelector('[data-mail]').href = 'mailto:info@miningshop.ru?subject=' +
          encodeURIComponent('Подбор оборудования') + '&body=' + encodeURIComponent(full);
      }
      build();
      if (note) note.oninput = build;
    }
    prev.addEventListener('click', function () { show(i - 1); });
    next.addEventListener('click', function () { show(i + 1); });
    show(0);
  }

  // --- короткие заявки (выкуп, трейд-ин, сборка) ---
  // Та же логика, что у подбора: собираем текст из полей и даём отправить его в Telegram или на почту.
  document.querySelectorAll('[data-lead]').forEach(function (form) {
    var subject = form.dataset.lead;
    function build() {
      var lines = [];
      form.querySelectorAll('input, select, textarea').forEach(function (el) {
        if (!el.value || (el.type === 'radio' && !el.checked)) return;
        var cap = el.closest('label') ? el.closest('label').querySelector('span') : null;
        lines.push((cap ? cap.textContent : el.name) + ': ' + el.value);
      });
      var text = subject + ' — заявка с сайта MiningShop\n' + lines.join('\n');
      form.querySelector('[data-tg]').href = 'https://t.me/miningshop?text=' + encodeURIComponent(text);
      form.querySelector('[data-mail]').href = 'mailto:info@miningshop.ru?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(text);
    }
    form.addEventListener('input', build);
    form.addEventListener('change', build);
    build();
  });

  // --- калькулятор видеопамяти ---
  // Оценка, а не точный расчёт: веса = параметры × биты / 8, кэш контекста растёт с длиной контекста и размером модели,
  // плюс 10 % и 0,5 ГБ на служебные буферы. Погрешность ±20 %, для подбора карты этого достаточно.
  var vr = document.querySelector('[data-vram]');
  if (vr) {
    var tiers = JSON.parse(vr.dataset.vram);
    function vrun() {
      var P = +vr.querySelector('[name=params]').value, b = +vr.querySelector('[name=bits]').value,
          ctx = +vr.querySelector('[name=ctx]').value;
      var w = P * b / 8, kv = ctx * (0.06 + 0.0045 * P) / 1024, total = w * 1.1 + kv + 0.5;
      var f = function (v) { return v.toLocaleString('ru-RU', { maximumFractionDigits: 1 }); };
      vr.querySelector('[data-o=weights]').textContent = f(w) + ' ГБ';
      vr.querySelector('[data-o=kv]').textContent = f(kv) + ' ГБ';
      vr.querySelector('[data-o=total]').textContent = f(total) + ' ГБ';
      var t = tiers.filter(function (x) { return x[0] >= total; })[0];
      vr.querySelector('[data-o=pick]').innerHTML = t ? t[1] : 'Нужен кластер из нескольких серверов — <a href="' + tiers[tiers.length - 1][2] + '">обсудим</a>.';
    }
    vr.querySelectorAll('input, select').forEach(function (el) { el.addEventListener('input', vrun); });
    vrun();
  }

  // --- калькулятор доходности ---
  // Считает только из того, что ввёл человек: хешпрайс (доход на единицу хешрейта в сутки)
  // берётся с открытых источников и меняется каждый день, поэтому зашивать его нельзя.
  var calc = document.querySelector('[data-calc]');
  if (calc) {
    var $ = function (n) { return calc.querySelector('[name=' + n + ']'); };
    var fmt = function (v, d) { return isFinite(v) ? v.toLocaleString('ru-RU', { maximumFractionDigits: d === undefined ? 0 : d }) : '—'; };
    var model = $('model');
    function applyModel() {
      var o = model.options[model.selectedIndex];
      if (o && o.dataset.h) { $('hash').value = o.dataset.h; $('power').value = o.dataset.p; $('unit').value = o.dataset.u; }
      run();
    }
    function run() {
      var h = +$('hash').value, p = +$('power').value, tariff = +$('tariff').value, hp = +$('hashprice').value,
          price = +$('price').value, pool = +$('pool').value / 100;
      var income = h * hp * (1 - pool);
      var energy = p / 1000 * 24 * tariff;
      var profit = income - energy;
      var q = function (s) { return calc.querySelector(s); };
      q('[data-o=income]').textContent = fmt(income) + ' ₽';
      q('[data-o=energy]').textContent = fmt(energy) + ' ₽';
      var pr = q('[data-o=profit]');
      pr.textContent = fmt(profit) + ' ₽';
      pr.className = profit >= 0 ? 'big pos' : 'big neg';
      q('[data-o=month]').textContent = fmt(profit * 30) + ' ₽';
      q('[data-o=payback]').textContent = profit > 0 && price > 0 ? fmt(price / (profit * 30), 1) + ' мес.' : 'не окупается';
      q('[data-o=breakeven]').textContent = h > 0 && hp > 0 ? fmt(income / (p / 1000 * 24), 2) + ' ₽/кВт·ч' : '—';
      q('[data-o=unit]').textContent = $('unit').value;
    }
    if (model) model.addEventListener('change', applyModel);
    calc.querySelectorAll('input').forEach(function (el) { el.addEventListener('input', run); });
    run();
  }
})();
