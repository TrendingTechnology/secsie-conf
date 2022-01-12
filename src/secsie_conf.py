import re


__version__ = 'v1.0.0'


SECTION_EX = re.compile(r'\[([a-zA-Z0-9]+)\]')
FLOAT_EX = re.compile(r'^(\d+[\.]\d*)$')
INT_EX = re.compile(r'^\d+$')


def _write_to_conf_(conf: dict, line, line_number: int, section=None) -> dict:
    key_value = [c.strip() for c in line.split('=')]
    try:
        key, value = key_value[0], key_value[1].split('#')[0].strip()
    except IndexError:
        raise SyntaxError(f'Syntax Error on line {line_number}: "{line}" bad section descriptor or value assignment')

    if ' ' in key:
        raise SyntaxError(f"Syntax Error on line {line_number}: Spaces not allowed in keys")

    if FLOAT_EX.match(value):
        value = float(value)
    elif INT_EX.match(value):
        value = int(value)

    if section is None:
        conf[key] = value
    else:
        if not conf.get(section, False):
            conf[section] = {}
        conf[section][key] = value
        
    return conf


def parse_config_file(conf_file: str) -> dict:
    with open(conf_file, 'r') as f:
        lines = [l.strip('\n') for l in f.readlines()]
    conf = {}
    c_section = None
    lineno = 0
    for line in lines:
        lineno += 1
        line = line.strip()
        if line == '':  # Skip blank lines
            continue
        if line.startswith('#') or line.startswith(';'):
            continue
        # Check to see if this is a section
        if SECTION_EX.match(line):
            c_section = SECTION_EX.findall(line)[0]
            continue
        conf = _write_to_conf_(conf, line, section=c_section, line_number=lineno)

    return conf


def generate_config(obj: dict, output_file: str = None) -> str:
    conf = "# auto-generated from JSON by secsie-conf\n\n"
    for key, value in obj.items():
        if isinstance(value, dict):
            conf += f"\n[{key}]\n"
            for k, v in value.items():
                conf += f"\t{k} = {v}\n"
            conf += "\n"
            continue
        conf += f"{key} = {value}\n"

    if output_file:
        with open(output_file, 'w') as f:
            f.write(conf)

    return conf