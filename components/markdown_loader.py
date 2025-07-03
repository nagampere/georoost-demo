# Markdownファイルの読み込み関数
def load_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
