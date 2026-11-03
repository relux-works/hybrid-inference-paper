"""Render structured tables; numerical calculations never depend on presentation."""
import csv
import io
import json
from .inputs import InputError


def cell(value):
    if isinstance(value, dict) and 'alarm' in value:
        return 'ALARM: ' + '; '.join(a['input'] + ': ' + a['reason'] for a in value['alarm'])
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, float):
        return '{:.6g}'.format(value)
    return '' if value is None else str(value)


def tex_escape(value):
    escapes = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
               '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
    return ''.join(escapes.get(c, c) for c in cell(value))


def render(result, format='md'):
    if format == 'json':
        return json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if format == 'legacy':
        if 'legacy_text' not in result:
            raise InputError('legacy formatter requires a historical scenario')
        return result['legacy_text']
    stream = io.StringIO(newline='')
    if format == 'csv':
        # One rectangular CSV across heterogeneous tables, preserving table and column identities.
        columns = list(dict.fromkeys([k for table in result['tables'] for k in table['columns']] + ['input', 'reason'])) if any(t.get('alarms') for t in result['tables']) else list(dict.fromkeys(k for table in result['tables'] for k in table['columns']))
        writer = csv.DictWriter(stream, fieldnames=['table'] + columns)
        writer.writeheader()
        for table in result['tables']:
            for row in table['rows']:
                writer.writerow({'table': table['name'], **{k: cell(v) for k, v in row.items()}})
            for alarm in table.get('alarms', []):
                writer.writerow({'table': table['name'] + ' ALARMS', **alarm})
        return stream.getvalue()
    if format not in ('md', 'tex'):
        raise InputError('unknown formatter: ' + format)
    for table in result['tables']:
        keys = list(table['columns'])
        headings = ['{} ({})'.format(k, table['columns'][k]) for k in keys]
        if format == 'tex':
            stream.write('% ' + table['name'].replace('\n', ' ') + '\n')
            stream.write('\\begin{tabular}{' + 'l' * len(keys) + '}\n\\toprule\n')
            stream.write(' & '.join(tex_escape(h) for h in headings) + ' \\\\\n\\midrule\n')
            for row in table['rows']:
                stream.write(' & '.join(tex_escape(row.get(k)) for k in keys) + ' \\\\\n')
            stream.write('\\bottomrule\n\\end{tabular}\n\n')
        else:
            escape = lambda v: cell(v).replace('|', '\\|').replace('\n', '<br>')
            stream.write('### ' + table['name'] + '\n\n')
            stream.write('| ' + ' | '.join(escape(h) for h in headings) + ' |\n')
            stream.write('| ' + ' | '.join('---' for _ in keys) + ' |\n')
            for row in table['rows']:
                stream.write('| ' + ' | '.join(escape(row.get(k)) for k in keys) + ' |\n')
            stream.write('\n')
        for alarm in table.get('alarms', []):
            message = 'ALARM: ' + alarm['input'] + ': ' + alarm['reason']
            stream.write(('% ' + message if format == 'tex' else '- ' + message) + '\n')
        if table.get('alarms'):
            stream.write('\n')
    for note in result.get('notes', []):
        stream.write(('% ' if format == 'tex' else '') + note + '\n')
    return stream.getvalue()
