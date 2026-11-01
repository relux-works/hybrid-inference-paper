"""python3 -m hybridcalc {list,run,sources,export}."""
import argparse
import sys
from .engine import run, scenarios
from .inputs import InputError
from .formatters import render


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    for command in ('run', 'sources', 'export'):
        child = commands.add_parser(command)
        child.add_argument('scenario', help='bundled scenario name or scenario JSON file')
        child.add_argument('--set', dest='overrides', action='extend', nargs='+', default=[], metavar='PATH=VALUE')
        child.add_argument('--strict', action='store_true', help='exit 1 after printing results if any metric alarms')
        if command == 'export':
            child.add_argument('--output', required=True, help='directory for one CSV per named table and audit sidecars')
        else:
            child.add_argument('--format', choices=('md', 'csv', 'json', 'legacy', 'tex'), default='md')
    args = parser.parse_args(argv)
    try:
        if args.command == 'list':
            for scenario in scenarios():
                print('{}\t{}'.format(scenario['name'], scenario['description']))
        else:
            result = run(args.scenario, args.overrides)
            status = 1 if (args.strict and result.get('alarms')) or ('computed_metrics' in result and result['computed_metrics'] == 0) else 0
            if args.command == 'export':
                import json
                from .export import write_tables
                manifest = write_tables(result, args.output)
                sys.stdout.write(json.dumps({'scenario': result['scenario'], 'tables': manifest['tables'], 'alarm_cells': manifest['alarm_cells'], 'output': args.output}, indent=2) + '\n')
                if status:
                    parser.exit(status)
                return
            if args.command == 'sources':
                alarms = result.get('alarms', [])
                result = {'scenario': result['scenario'], 'alarms': alarms, 'tables': [{'name': 'Used numeric inputs',
                    'columns': {'path': 'text', 'value': 'number or enum', 'unit': 'text', 'provenance': 'text'},
                    'rows': result['sources']}, {'name': 'Measured files',
                    'columns': {'path': 'text', 'sha256': 'text', 'provenance': 'text'},
                    'rows': result['files'], 'alarms': alarms}]}
            sys.stdout.write(render(result, args.format))
            if status:
                parser.exit(status)
    except (InputError, OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, ArithmeticError) as exc:
        parser.exit(2, 'hybridcalc: {}\n'.format(exc))


if __name__ == '__main__':
    main()
