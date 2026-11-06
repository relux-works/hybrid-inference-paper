# Paper: the closed contour, correct wording for RC4 and a new subsection (run hybrid-c-r21n-261105)

Continue from your r21m head. The owner decided, and the analyst agreed, how the closed contour is to be framed. This
also closes the external reviewer's main point.

## For RC4, while the calculations are pending (engine run 26)

1. **Fix the wording.**
   - The threshold «с 5 человек при средней, с 2 при тяжёлой» applies to a company that keeps the open model in-house
     for part of its tasks (s = 20%).
   - The s = 20% calculation is legitimate for a closed contour only if the other 80% is served by an internal large
     model. That model's cost is the same in both variants; say so explicitly.
   - The conclusion for a fully closed contour (s = 100%) and for the mixed scheme awaits engine run 26. Never present
     the 20% thresholds as the fully closed result.
   - Apply this in both abstracts, the introduction, the conclusion and section 8.
2. **A new section-8 subsection «Закрытый контур».** Use the thesis text below, in the paper's style, and the map
   table. Mark every unmeasured element as pending. If engine run 25 has been accepted by the time you write, use its
   s = 100% Qwen numbers; otherwise mark them pending.
3. **In the introduction and the conclusion,** give the closed contour one sentence in the «Кому подходит» block.
4. **Put the cloud class inside the contour under «Перспективы».**
5. **Add to the pending list:**
   - GLM on a Studio (decode and prefill);
   - GLM prefill on a B300;
   - the M5 Ultra (extrapolated from the M5 Max by owner decision);
   - the Studio 512 GB price and configuration;
   - the middle class's task share (an input scenario).

The thesis (the analyst's text; adapt the style, keep the content):

> Закрытый контур. Если данные не могут покидать контур, гибрид сравнивается не с облачным API, а с внутренним инференсом, и выбор идёт в два шага. Сначала организация выбирает класс моделей. Модели облачной весовой категории, от сотен миллиардов до триллионов параметров, работают только на серверных кластерах: в память клиента они не помещаются, и гибрид для них неприменим. Для моделей среднего класса — плотных около 30 млрд параметров и MoE около 300 млрд — есть два пути. Первый — свой кластер, который делает и prefill, и генерацию. Второй — гибрид: серверы только читают контекст, а генерируют клиенты, M5 Max для моделей около 30 млрд и Mac Studio M5 Ultra на 256–512 ГБ для MoE. Если клиентов нет, их покупка входит в цену. Возможна и смешанная схема: большая модель на внутреннем кластере решает сложные задачи, а средняя через гибрид — остальные. Тогда доля s означает долю задач, переданных средней модели внутри контура, а не в облако.

The map:

| Класс модели | Что можно держать в контуре | Гибрид |
|---|---|---|
| Облачный: сотни млрд – трлн | только свой кластер из многоузловых B300 | неприменим |
| ~30 млрд, плотная (Qwen3.8-27B) | свой кластер или гибрид + M5 Max 64/128 ГБ | измерен |
| ~300 млрд, MoE (GLM-5.3-Flash) | свой кластер (2 B300 на реплику) или гибрид + Studio 256/512 ГБ | только расчёт |

## Rules

- The same gates and style rules as r21m.
- CPU only. `TMPDIR` on disk, `PYTHONDONTWRITEBYTECODE=1`. Free disk stays above **28 GiB** (`df -BG`).
- Signed commits with the trailer `Co-authored-by: Codex gpt-6.1-sol <noreply@openai.com>`. No session links, no push,
  no tag.
- Send a short summary to `agents1_hybrid_orch` in #hybrid, topic prototype-go: the head, the PDF path, and every
  place the closed-contour wording changed.
