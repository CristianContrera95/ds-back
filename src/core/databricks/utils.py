import json
from pathlib import Path
from tempfile import NamedTemporaryFile


def extract_content(tmp_file, name_view='notebook'):
    with open(tmp_file, 'rb') as fp:
        exported_content = fp.read()

    data = json.loads(exported_content).get("views")
    for element in data:
        if (name_view == 'notebook' and element.get('type').lower() == 'notebook') or \
                (element.get("name") == name_view) or (name_view == 'ALL'):
            with NamedTemporaryFile(mode='w', delete=False, suffix=".html") as tmp:
                tmp.write(str(element.get("content", "")))
                tmp_path = Path(tmp.name)
            return tmp_path
