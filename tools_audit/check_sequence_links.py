# -*- coding: utf-8 -*-
"""Проверка КОРРЕКТНОСТИ СВЯЗЕЙ диаграммы последовательности ЛР2.

Проверяется не геометрия, а семантика связей:
  1) нумерация сообщений — подряд, без пропусков и повторов;
  2) парность «синхронный вызов ↔ возврат» по принципу стека (LIFO):
     возврат обязан закрывать ровно тот вызов, который был последним;
  3) все ветви alt возвращают управление в одно и то же состояние стека
     (иначе продолжение после фрагмента не определено);
  4) тело loop сбалансировано само по себе (иначе цикл «течёт»);
  5) каждый объект (не актёр) действует только внутри своей полосы активации;
  6) каждая полоса активации начинается на входящем вызове и заканчивается
     на своём возврате;
  7) асинхронные сообщения не требуют возврата, но и не открывают вызов.
"""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_lab2_uml as g


def collect():
    g.sequence_diagram()                      # заполняет g.SEQ
    sq = g.SEQ
    msgs = []
    for it in sq.items:
        if it[0] == 'msg':
            _, a, b, kind, y, text = it
            msgs.append(dict(a=a, b=b, kind=kind, y=y, text=text))
        else:
            _, a, y, text = it
            msgs.append(dict(a=a, b=a, kind='self', y=y, text=text))
    msgs.sort(key=lambda m: m['y'])
    return sq, msgs


def num(text):
    m = re.match(r'(\d+)\.', text)
    return int(m.group(1)) if m else None


def walk(msgs, stack, problems, where):
    """Прогон сообщений со стеком вызовов. Возвращает конечный стек."""
    stack = list(stack)
    for m in msgs:
        tag = '[%s] %d. %s' % (where, num(m['text']) or 0, m['text'][:58])
        if m['kind'] == 'sync':
            stack.append((m['a'], m['b'], num(m['text'])))
            continue
        if m['kind'] in ('self', 'async'):
            continue
        if m['kind'] == 'return':
            if not stack:
                problems.append('%s — возврат без вызова' % tag)
                continue
            caller, callee, nth = stack.pop()
            if (caller, callee) != (m['b'], m['a']):
                problems.append(
                    '%s — возврат не тому: ожидался возврат %d→%d (вызов %d), '
                    'а нарисован %d→%d' % (tag, callee, caller, nth, m['a'], m['b']))
            continue
        problems.append('%s — неизвестный вид сообщения %r' % (tag, m['kind']))
    return stack


def frag_ranges(sq):
    """Границы операндов alt и тело loop: (вид, [(y0, y1), ...])"""
    out = []
    for (x0, x1, op, guards, in_tab, y0, y1) in sq.frags:
        if op == 'alt':
            edges = [g_[0] for g_ in guards] + [y1]
            out.append(('alt', [(edges[k], edges[k + 1]) for k in range(len(edges) - 1)]))
        else:
            out.append((op, [(y0, y1)]))
    return out


def main():
    sq, msgs = collect()
    problems = []
    names = [h[1].replace('\n', ' ') for h in sq.heads]
    actors = {i for i, h in enumerate(sq.heads) if h[0] == 'actor'}

    # 1. нумерация
    nums = [num(m['text']) for m in msgs]
    expect = list(range(1, len(msgs) + 1))
    if nums != expect:
        problems.append('нумерация сообщений не подряд: %s' % nums)

    # границы фрагментов
    ranges = frag_ranges(sq)
    alt = next((r for kind, r in ranges if kind == 'alt'), None)
    loop = next((r for kind, r in ranges if kind == 'loop'), None)

    def inside(m, lo, hi):
        return lo <= m['y'] < hi

    # 2. линейная часть до alt
    y_alt_start = alt[0][0] if alt else None
    pre = [m for m in msgs if y_alt_start is None or m['y'] < y_alt_start]
    stack = walk(pre, [], problems, 'до alt')

    # 3. ветви alt — каждая из одного и того же состояния
    if alt:
        ends = []
        for k, (lo, hi) in enumerate(alt):
            part = [m for m in msgs if inside(m, lo, hi)]
            # тело вложенного loop внутри ветви проверяем отдельно
            if loop:
                body = [m for m in part if inside(m, loop[0][0], loop[0][1])]
                if body:
                    st0 = walk([m for m in part if m['y'] < loop[0][0]], list(stack),
                               problems, 'ветвь %d до loop' % (k + 1))
                    st1 = walk(body, st0, problems, 'loop')
                    if st1 != st0:
                        problems.append('тело loop не сбалансировано: открыто %d вызов(ов)'
                                        % (len(st1) - len(st0)))
                    rest = [m for m in part if m['y'] >= loop[0][1]]
                    end = walk(rest, st1, problems, 'ветвь %d после loop' % (k + 1))
                else:
                    end = walk(part, stack, problems, 'ветвь %d' % (k + 1))
            else:
                end = walk(part, stack, problems, 'ветвь %d' % (k + 1))
            if end != stack[:len(end)]:
                problems.append('ветвь %d закрывает вызовы не по порядку стека' % (k + 1))
            ends.append(end)
        if len({tuple(e) for e in ends}) > 1:
            problems.append('ветви alt возвращают управление в разное состояние: %s'
                            % [e[-1] if e else None for e in ends])
        stack = ends[0]

    # 4. продолжение после alt
    post = [m for m in msgs if alt and m['y'] >= alt[-1][1]]
    stack = walk(post, stack, problems, 'после alt')
    if stack:
        problems.append('остались незакрытые вызовы: %s'
                        % ['%d→%d (№%s)' % (c, k, n) for c, k, n in stack])

    # 5. объекты действуют только в своей полосе активации
    bars = {}
    for (i, y0, y1, level) in sq.acts:
        bars.setdefault(i, []).append((y0, y1))
    for m in msgs:
        for side in ('a', 'b'):
            i = m[side]
            if i in actors:
                continue
            if not any(y0 - 0.5 <= m['y'] <= y1 + 0.5 for y0, y1 in bars.get(i, [])):
                problems.append('%d. %s — участник :%s действует вне полосы активации'
                                % (num(m['text']) or 0, m['text'][:46], names[i]))

    # 6. полосы: первое сообщение — входящий вызов, последнее — свой возврат
    for (i, y0, y1, level) in sq.acts:
        here = [m for m in msgs if abs(m['y'] - y0) < 0.5 or abs(m['y'] - y1) < 0.5]
        first = [m for m in msgs if abs(m['y'] - y0) < 0.5]
        last = [m for m in msgs if abs(m['y'] - y1) < 0.5]
        if not any(m['kind'] == 'sync' and m['b'] == i for m in first):
            problems.append('полоса :%s (%d…%d) начинается не на входящем вызове'
                            % (names[i], y0, y1))
        # полоса закрывается действием самого объекта: возвратом, асинхронной
        # отправкой (уведомление) — но не приходом чужого сообщения
        if not any(m['a'] == i and m['kind'] in ('return', 'async', 'sync') for m in last):
            problems.append('полоса :%s (%d…%d) заканчивается не действием объекта'
                            % (names[i], y0, y1))

    # ---- отчёт -----------------------------------------------------------
    print('связей: %d, участников: %d, полос активации: %d'
          % (len(msgs), len(sq.heads), len(sq.acts)))
    print()
    for m in msgs:
        arrow = {'sync': '──▶', 'return': '┄┄▷', 'async': '──▷', 'self': '↺'}[m['kind']]
        right = '' if m['kind'] == 'self' else ' %s %s' % (arrow, names[m['b']])
        print('%s. %-46s  %-22s%s' % (str(num(m['text'])).rjust(2),
                                      m['text'][:46].split('. ', 1)[-1],
                                      names[m['a']][:22], right))
    print()
    if problems:
        print('НАЙДЕНО ПРОБЛЕМ: %d' % len(problems))
        for p in problems:
            print('  !', p)
        return 1
    print('связи корректны: нумерация подряд, каждый вызов закрыт своим возвратом,')
    print('ветви alt сходятся, тело loop сбалансировано, объекты действуют только')
    print('внутри своих полос, каждая полоса открыта вызовом и закрыта возвратом.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
